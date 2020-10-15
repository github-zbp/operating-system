# coding=utf-8

import select, socket

# 服务端代码，该代码不能再windows中运行，因为windows中没有epoll的系统调用

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 8000))
server.listen()
server.setblocking(False)

print("服务器启动成功")

# 创建epoll对象，相当于执行了 epoll_create 在内核中开辟了一块空间用于记录fd事件
epoll = select.epoll()

# 注册要监听的fd事件，相当于调用 epoll_ctl 将fd的事件写入内核空间中。
epoll.register(server.fileno(), select.EPOLLIN)     # 监听server套接字的可读事件，第一参传的是服务端socket的文件描述符，文件描述符是一个整型数字

# 存储要监听的socket
monitored_socket = { server.fileno():server}

# 存储客户端发送过来的消息
client_msg = {}

timeout = 10

while True:
    # 等待fd的事件就绪（触发事件），相当于执行epoll_wait()，这个过程是阻塞的，上面的setblocking(False)是控制套接字的操作不阻塞，但是不能控制epoll不阻塞
    # 这里可以传入阻塞的超时时间timeout, 不传则一直阻塞; 如果没有事件就绪且超过超时时间则返回null;如果有事件就绪，则返回一个列表，每个列表放着一个元祖，元组放着事件就绪的fd和具体事件类型
    events = epoll.poll(timeout)

    if not events:
        print("无事件就绪")
        print(events)
    else:
        print("有 %s 个事件就绪" % len(events))

    for fd, event in events:
        ready_socket = monitored_socket[fd]     # 根据fd获取就绪的socket对象

        if ready_socket == server:      # 如果就绪fd是server，说明server可读事件就绪，表示有客户端连接
            client, addr = server.accept()     # 非阻塞，而且一定能接收到连接

            client_fd = client.fileno()

            print("客户端 %s 建立连接成功" % str(client_fd))

            client.setblocking(False)

            # 先监听客户端的可读事件
            epoll.register(client_fd, select.EPOLLIN)
            monitored_socket[client_fd] = client
            client_msg[client_fd] = []      # 保存该客户端的所有发送过来的消息

        elif event == select.EPOLLHUP:      # 如果客户端关闭连接
            ready_socket.close()

            epoll.unregister(fd)    # 不再监听该客户端的事件

            del monitored_socket[fd]

            del client_msg[fd]

            print("客户端 %s 关闭连接" % str(fd))

        elif event == select.EPOLLIN:  # 如果客户端读事件就绪
            msg = ready_socket.recv(1024)

            if msg:
                print("接收到客户端 %s 的消息 %s" % (str(fd), msg.decode("utf-8")))

                client_msg[fd].append(msg)

                # 修改监听事件为写事件,因为客户端发送消息过来之后我想将消息马上原样发送回给客户端
                epoll.modify(fd, select.EPOLLOUT)

        elif event == select.EPOLLOUT: # 如果客户端写事件就绪，其实只要客户端的输入缓冲区没满应该就满足写事件就绪（所谓的客户端写事件就绪是客户端可以被写而不是可以去写）
            try:
                msg = client_msg[fd].pop()
            except:
                print("客户端 %s 消息列表为空" % str(fd))
                epoll.modify(fd, select.EPOLLIN)  # 如果将客户端的所有消息都发回去了，就改回监听客户端读事件
            else:
                ready_socket.send(msg)







