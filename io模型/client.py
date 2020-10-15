# coding=utf-8

from threading import Thread, currentThread
import socket

# 客户端代码

# 创建套接字
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 绑定ip和端口
ip = "127.0.0.1"
port = 8000

client.connect((ip, port))

while True:
    msg = input()
    if msg:
        client.send(msg.encode("utf-8"))
    else:   # 如果直接输入换行则断开连接
        client.close()
        break