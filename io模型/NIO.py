# coding=utf-8

from threading import Thread, currentThread
import socket
from time import sleep

# 服务端代码

# 创建套接字
server = socket.socket()

# 绑定ip和端口
ip = "127.0.0.1"
port = 8000
server.bind((ip, port))

server.listen(3)                # 只允许最多3个客户端连接
server.setblocking(False)       # 非阻塞socket
print("server服务已开启")

clients = dict()    # 用于存储所有建立了连接的客户端
no = 1          # 客户端编号
while True:
    try:
        client,addr = server.accept()    # 接收连接，非阻塞, 如果没有接收到连接则抛出一个异常
        print("接收到客户端")
        clients[no] = client
        no += 1
        client.setblocking(False)       # 设置客户端socket为非阻塞，这样后面调用recv就是非阻塞的了
    except BlockingIOError:
        # print("未接收到客户端")
        sleep(0.1)


    for client_no in list(clients.keys()):     # 遍历所有连接的客户端，接收他们发送的消息,这里要用list函数转一下clients.keys()，否则在删除字典中的客户端时再循环会报错说字典遇到改变
        each_client = clients[client_no]
        try:
            msg = each_client.recv(1024)      # 非阻塞,如果没有接收到消息则抛出一个异常

            if not msg:  # 如果发送空消息表示连接已断开
                each_client.close()
                del clients[client_no]  # 从列表中移除该客户端
                print("客户端 %s 断开连接" % str(client_no))
            else:
                print("客户端 %s 发送消息：%s" % (str(client_no), msg.decode('utf-8')))
                sleep(0.1)
        except BlockingIOError:     # 客户端未发送消息
            pass

