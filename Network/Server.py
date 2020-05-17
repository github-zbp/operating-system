# coding=utf-8

import socket
import os,sys,json

sys.path.append("..")

from ThreadTool.ThreadPool import ThreadPool as tp
from ThreadTool.Task import AsyncTask
from IPParser import IPParser
from UDPParser import UDPParser

class ProcessTask(AsyncTask):
    def __init__(self,packet,*args,**kwargs):
        self.packet=packet
        super(ProcessTask, self).__init__(func=self.process,*args,**kwargs)

    # 定义任务函数
    def process(self):
        headers={
            "network_header":None,      # 网络层报文的头部
            "transport_header":None     # 传输层报文的头部
        }
        ip_header = IPParser.parse(self.packet)
        headers['network_header'] = ip_header

        if ip_header['protocol']==17:
            udp_header = UDPParser.parse(self.packet)
            headers["transport_header"]=udp_header

        return headers



class Server:
    def __init__(self):
        # 使用ipv4协议，套接字类型为原始套接字，工作协议是IP协议(意味着下面接收到的包packet已经给你处理成是IP数据包)
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_IP)

        # 绑定IP和端口
        self.ip = "192.168.0.106"   # 设置服务器的IP，就是自己这台电脑的IP
        self.port = 80
        self.sock.bind((self.ip,self.port))

        # 使用网卡模式为混杂模式
        self.sock.ioctl(socket.SIO_RCVALL,socket.RCVALL_ON)

        # 创建线程池和10个线程
        self.pool = tp(10)

        # 启动线程,等待任务进入队列
        self.pool.start()

    def loop_server(self):
        # 不停的接收报文，限定每65535为一个报文。将报文做成任务放到任务队列处理交给线程池中的线程处理
        # 也就是说报文的处理是多线程的是并发的
        while True:
            packet,addr = self.sock.recvfrom(65535)

            # 一个报文的解析作为一个任务
            task = ProcessTask(packet)

            # 任务放入队列
            self.pool.put_task(task)

            # 获取任务处理结果
            result = task.get_result()
            result = json.dumps(    # 格式化一下结果
                result,
                indent=4    # 缩进4个字节
            )

if __name__ == "__main__":
    server = Server()
    server.loop_server()    # 启动服务，监听和接收报文