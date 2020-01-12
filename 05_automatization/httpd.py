import logging
import argparse
import socket
import threading
import sys
import select

import config
from connections import HttpConnectionHandler
from http_handler import set_root


class Worker(threading.Thread):
    def __init__(self, id,  socket, HandlerClass):
        super(Worker, self).__init__()
        self.socket = socket
        self.handler_class = HandlerClass
        self.id = id

    def run(self):
        self.socket.listen(config.BACKLOG_CONNECTIONS)
        self.socket.setblocking(0)
        logging.info(f'Worker {self.id} start listen')

        epoll = select.epoll()
        epoll.register(self.socket.fileno(), select.EPOLLIN)

        handlers = {}

        while True:
            events = epoll.poll(config.CONNECTION_TIMEOUT)
            for fileno, event in events:
                if fileno == self.socket.fileno():
                    try:
                        while True:
                            conn, addr = self.socket.accept()
                            conn.setblocking(0)
                            handler = self.handler_class(conn, addr)
                            handlers[handler.fileno()] = handler
                            epoll.register(handler.fileno(),
                                           select.EPOLLIN | select.EPOLLET)
                    except:
                        continue

                elif event & select.EPOLLIN:
                    handler = handlers[fileno]
                    try:
                        while handler.ready_to_receive:
                            handler.receive()

                    except socket.error:
                        pass

                    flags = self._modify_flags(handler, epoll)
                    if flags == 0:
                        handler.shutdown()

                elif event & select.EPOLLOUT:
                    handler = handlers[fileno]
                    try:
                        while handler.need_transmit():
                            handler.send()
                    except socket.error:
                        pass

                    flags = self._modify_flags(handler, epoll)
                    if flags == 0:
                        handler.shutdown()

                elif event & select.EPOLLHUP:
                    epoll.unregister(fileno)
                    handler = handlers[fileno]
                    handler.close()
                    del handlers[fileno]

    def _modify_flags(self, handler, epoll):
        flags = select.EPOLLIN if handler.ready_to_receive else 0
        if handler.need_transmit():
            flags |= select.EPOLLOUT

        if flags != 0:
            flags |= select.EPOLLET

        epoll.modify(handler.fileno(), flags)
        return flags


def start_server(addr, port, n_workers):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((addr, port))
    workers = []
    for i in range(n_workers):
        w = Worker(i, s, HttpConnectionHandler)
        workers.append(w)
        w.start()

    for w in workers:
        w.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Training web server')
    parser.add_argument('-a', '--address', type=str,
                        help='server address', default=config.ADDRESS)
    parser.add_argument('-p', '--port', type=int,
                        help='server port', default=config.PORT)
    parser.add_argument('-w', '--workers', type=int,
                        help='number of workers', default=config.WORKERS)
    parser.add_argument('-r', '--document_root', type=str,
                        help='document root', default=config.DOCUMENT_ROOT)
    parser.add_argument('-l', '--logfile', type=str,
                        help='log file', default=config.LOG_FILE)

    args = parser.parse_args()

    log_file = args.logfile or config.LOG_FILE

    logging.basicConfig(filename=log_file, format=config.LOG_FMT,
                        level=config.LOG_LEVEL, datefmt=config.LOG_DATE_FMT)

    try:
        set_root(args.document_root)
    except:
        sys.exit('document root path not found')

    try:
        start_server(args.address, args.port, args.workers)
    except Exception as e:
        logging.exception(str(e))
