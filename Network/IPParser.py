# coding=utf-8

import struct,socket

# IP报文解析器
class IPParser:
    IP_HEADER_LENGTH=20     # IP 报文头部的长度是固定的，20个字节

    @classmethod
    def parse_ip_header(cls,ip_header):
        """
        IP 报文格式（IP报文头部的每一行都有32位长度，即4个字节）
        头部第1行 4位IP-Version 4位IP头长度 8位服务类型 16位总长度
        头部第2行 16位标识符  3位标记位 3位片偏移
        头部第3行 8位TTL  8位协议   16位IP头校验和
        头部第4行 32位源IP地址
        头部第5行 32位目的IP地址

        这里需要解析第1,3,4,5行的内容
        报文中的以上信息全部都是用二进制表示的
        """

        # struct最小只能解析一个字节，也就是8位，无法直接解析4位

        # 解析第一行,ip_header[:4]是获取报文头部的前四个4截，也即是第一行
        line1 = struct.unpack(">BBH",ip_header[:4])  # 返回一个3个元素的元组,三个元素分别是8个位(一个字节)，8个位和16个位（2个字节）的数据
        ip_version=line1[0] >> 4   # line[0]包含了八个位，我想获取前4个位需要做二进制的位移操作(获取到的二进制位会自动转为10进制)
        iph_length=line1[0] & 15   # line[0]中的8个位和 00001111 （15） 做与运算即可获取后4个位的二进制(会自动转为10进制)
        packet_length=line1[2]

        # 解析第三行
        line3 = struct.unpack(">BBH",ip_header[8:12])
        TTL = line3[0]
        protocol = line3[1]
        iph_checksum = line3[2]

        # 解析第四第五行
        line4 = struct.unpack(">4s",ip_header[12:16])   # 返回一个只有一个元素的元组
        line5 = struct.unpack(">4s",ip_header[16:20])
        src_ip = socket.inet_ntoa(line4[0])     # 将byte类型的二进制转为点分十进制的IP
        des_ip = socket.inet_ntoa(line5[0])

        # 返回以下信息,得到的以下信息都会被unpack转为10进制
        return {
            'ip_version':ip_version,
            'iph_length':iph_length,
            "packet_length":packet_length,    # 数据包数总长度
            "TTL":TTL,         # 过期次数
            "protocol":protocol,     # 报文的协议(TCP/UDP/...),6是TCP，17是UDP
            "iph_checksum":iph_checksum,     # 校验和
            "src_ip":src_ip,          # 源IP
            "des_ip":des_ip       # 目的IP
        }

    @classmethod
    def parse(cls,packet):
        ip_header = packet[:cls.IP_HEADER_LENGTH]

        return cls.parse_ip_header(ip_header)