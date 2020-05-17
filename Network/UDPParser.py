# coding=utf-8

import struct

# UDP 报文解析器

class UDPParser:
    IP_HEADER_LENGTH=20
    UDP_HEADER_LENGTH=8

    """
    UDP头部共8个字节的长度
    第一行 16为源端口 16位目的端口
    第二行 16位UDP数据长度 16位校验和
    """
    @classmethod
    def parse_udp_header(cls,udp_header):
        udp_header = struct.unpack(">HHHH",udp_header)

        return {
            "src_port":udp_header[0],
            "des_port":udp_header[1],
            "udp_length":udp_header[2],
            "udp_checksum":udp_header[3]
        }

    @classmethod
    def parse(cls,packet):
        # 这个packet还是ip数据包，udp或者tcp数据包是放在IP报文内容中的
        # packet的前20个字节是ip报文头部，所以20个字节后的内容就是TCP或UDP的内容
        udp_header = packet[cls.IP_HEADER_LENGTH:cls.IP_HEADER_LENGTH+cls.UDP_HEADER_LENGTH]

        return cls.parse_udp_header(udp_header)

