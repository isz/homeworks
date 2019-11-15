import os
from collections import namedtuple
from datetime import datetime

def test_exc():
    raise Exception('haha')


def exec_test():
    test_exc()


# try:
#     exec_test()
# except Exception as e:
#     print(str(e))

# print(os.listdir('vsdv'))

a=namedtuple('Car',['col','y'])
c=a('red', 1982)

print(c.col, c.y)

print(datetime.strptime('00031312', '%Y%m%d'))