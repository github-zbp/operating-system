# coding=utf-8

import socket
import select
# from select import select

# 服务端代码

# 创建套接字
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 绑定ip和端口
ip = "127.0.0.1"
port = 8000
server.bind((ip, port))

server.listen(3)                # 只允许最多3个客户端连接
server.setblocking(False)       # 非阻塞socket

rfd = set()     # 存放要监控的文件描述符，这里监控的是达到可读状态的socket
wfd = set()     # 存放要监控的文件描述符，这里监控的是达到可写状态的socket
efd = set()     # 存放要监控的文件描述符，这里监控的是出现异常状态的socket
rfd.add(server)

client_no = 1
clients = dict()

while True:
    print("开始select监控")
    # 获取所有处于可读，可写状态和发生异常的socket（他这里返回的到底是事件还是socket还不好说，可以验证一下）
    r_sockets, w_sockets, e_sockets = select.select(rfd, wfd, efd)      # 还可以传第四参超时时间，如果不传第四参，则select方法是阻塞的，执行到select就会一直阻塞直到有socket的状态改变；如果设了第4参为1，则执行select会阻塞1秒，1秒内没有socket改变状态就会循环1次再执行select

    # 这里我只关注可读的socket
    for r_socket in r_sockets:
        if r_socket == server:   # 如果是服务器socket可读，说明有连接进来了，此时可以去直接接收连接
            client, addr = r_socket.accept()      # 不阻塞，而且肯定可以接收到连接
            rfd.add(client)     # 将连接的客户端添加到要监控的集合中

            clients[client] = client_no
            print("客户端 %s 连接成功" % str(client_no))

            client_no += 1

        else:   # 如果是客户端socket可读，说明客户端发送消息到服务端
            msg = r_socket.recv(1024)       # 不阻塞

            if not msg:
                print("客户端 %s 断开连接" % str(clients[r_socket]))
                rfd.remove(r_socket)
            else:
                print("客户端 %s 发送消息：%s" % (str(clients[r_socket]), msg.decode('utf-8')))