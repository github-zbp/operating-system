# coding=utf-8

from threading import Thread, currentThread
import socket

# 服务端代码

# 创建套接字
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 绑定ip和端口
ip = "127.0.0.1"
port = 8000
server.bind((ip, port))

# 监听套接字
server.listen()

print("服务已开启")

def contact(client):
    print("客户端 %s 已成功连接" % currentThread().name)

    msg = client.recv(1024).decode("utf-8")  # 接收客户端发送到服务端的消息，这里也会收到阻塞
    while msg:     # 允许接收客户端发送多次消息，如果对方发送空字符，则认为客户端断开连接，此时结束该线程
        print("客户端 %s 发送信息：%s" % (currentThread().name, msg))
        msg = client.recv(1024).decode("utf-8")

    print("客户端 %s 断开连接" % currentThread().name)

while True:
    print("等待接收客户端连接")
    client,addr = server.accept()    # 接受连接, 这里会受到阻塞

    # 创建线程用于客户端和服务端通信
    thread = Thread(target=contact, args=(client,))
    thread.start()

