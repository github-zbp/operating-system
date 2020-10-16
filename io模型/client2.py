# coding=utf-8

from threading import Thread, currentThread
import socket

# 客户端代码

# 创建套接字
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 绑定ip和端口
ip = "127.0.0.1"
port = 8088

client.connect((ip, port))

def getResponse():
    while True:     # 开一个线程用于接收服务器返回的消息
        try:
            response = client.recv(1024)
            print(response.decode("utf-8"))
        except:     # 如果主线程关闭客户端socket则recv会报错，此时break跳出循环，结束该线程即可
            print("子线程由于client断开连接而退出")
            break

thread_for_response = Thread(target=getResponse)
thread_for_response.start()

while True:
    msg = input()
    if msg:
        client.send(msg.encode("utf-8"))
        print("msg:" + msg)
    else:   # 如果直接输入换行则断开连接
        client.close()      # 关闭套接字断开连接
        print("client close")
        # client.shutdown(socket.SHUT_RDWR)
        break
