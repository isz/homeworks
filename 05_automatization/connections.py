import socket
import logging

from http_handler import parse_http_request, handle_http


MAX_HTTP_HEADER_SIZE = 2*1024


class ConnectionHandler():
    CHUNK_SIZE = 1024

    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        self.ready_to_receive = True
        self.receive_buffer = b''
        self.response = b''

    def fileno(self):
        return self.connection.fileno()

    def receive(self):
        buf = self.connection.recv(self.CHUNK_SIZE)
        if len(buf) == 0:
            self.ready_to_receive = False
            self.response = b''
            return

        self.receive_buffer += buf
        if b'\n' in self.receive_buffer:
            request = self.receive_buffer.split(b'\n')[0]

            if request == b'by':
                self.ready_to_receive = False
                self.response += b'goodby\n'
            else:
                t = request+b'\n'
                self.response += t
                self.receive_buffer = self.receive_buffer[len(t):]

    def send(self):
        writed = self.connection.send(self.response)
        self.response = self.response[writed:]

    def shutdown(self):
        self.connection.shutdown(socket.SHUT_RDWR)

    def close(self):
        self.connection.close()

    def need_transmit(self):
        return len(self.response) != 0


class HttpConnectionHandler(ConnectionHandler):
    def __init__(self, *args, **kwargs):
        super(HttpConnectionHandler, self).__init__(*args, **kwargs)
        self.bytes_to_reveive = self.CHUNK_SIZE
        self.http_request = None

    def receive(self):
        buf = self.connection.recv(self.bytes_to_reveive)
        if len(buf) == 0:
            self.ready_to_receive = False
            self.response = b''
            return
        self.receive_buffer += buf

        if self.http_request is None:
            ind = self.receive_buffer.find(b'\r\n\r\n')
            if ind >= 0:
                self.http_request = parse_http_request(
                    self.receive_buffer[:ind])

                self.receive_buffer = self.receive_buffer[ind+4:]

                bytes_to_reveive = self.http_request.get('Content-Length', 0)
                if bytes_to_reveive == 0:
                    self.ready_to_receive = False
                    self.response += handle_http(self.http_request)
                    self.http_request = None
                else:
                    self.bytes_to_reveive = bytes_to_reveive

            elif len(self.receive_buffer) > MAX_HTTP_HEADER_SIZE:
                self.ready_to_receive = False
                self.response = b''
                return
        else:
            self.bytes_to_reveive -= len(buf)
            if self.bytes_to_reveive == 0:
                self.ready_to_receive = False
                length = self.http_request.get['Content-Length']
                self.http_request['body'] = self.receive_buffer[:length]
                self.receive_buffer = self.receive_buffer[length:]
                self.response += handle_http(self.http_request)
