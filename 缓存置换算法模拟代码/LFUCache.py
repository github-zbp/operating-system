# coding=utf-8

from DoubleLinkedList import DoubleLinkedList,Node
import random

# 频率节点，这种节点处理记录空间地址key和数据value外，还记录着空间在缓存中的访问次数freq
class FreqNode(Node):
    def __init__(self,key,value):
        self.freq=0
        super(FreqNode,self).__init__(key,value)

    def __str__(self):
        return "{%s,%s,%s}" % (self.key,self.value,self.freq)

    def __repr__(self):
        return "{%s,%s,%s}" % (self.key,self.value,self.freq)


class LFUCache:
    def __init__(self,capacity,ram):
        self.ram=ram
        self.capacity=capacity
        self.map={}     # 存放节点 FreqNode
        self.size=0
        self.dll_map={}     # 存放链表的字典，以访问次数为key

    # 更新某个节点的访问次数
    def __update_freq(self,node):
        self.dll_map[node.freq].remove(node)
        if self.dll_map[node.freq].size==0:
            del self.dll_map[node.freq]

        node.freq+=1

        if node.freq not in self.dll_map:   # 如果某一个频率的链表不存在就建一个
            self.dll_map[node.freq] = DoubleLinkedList()

        self.dll_map[node.freq].push(node)      # 压到尾部

    def __getFromRam(self,key):
        if key not in self.ram:
            return False

        node = self.ram[key]
        self.put(key,node.value)   # 进行主存内存置换

        return node

    def get(self,key):
        key=str(key)

        # 如果命中缓存
        if key in self.map:
            node = self.map[key]
            self.__update_freq(node)    # 改变node的访问次数，做+1操作
        else:   # 未命中缓存
            node = self.__getFromRam(key)

        if node:
            return node.value
        else:
            return False

    # CPU或者主存写入数据到高速缓存
    def put(self,key,value):
        key = str(key)

        # 分为命中缓存和没有命中
        if key in self.map:
            self.map[key].value=value
            self.__update_freq(self.map[key])
        else:
            # 两种情况：缓存没满和缓存满了
            if self.size==self.capacity:    # 存满了
                # 先将访问最少的节点从链表和map中删掉
                min_freq = min(self.dll_map)    # 获取最小的访问次数
                old_node = self.dll_map[min_freq].shift()  # 从头部弹出
                self.map.pop(old_node.key)

                old_node.freq=0     # 该节点的访问数清零
                self.ram[old_node.key]=old_node
                self.size-=1

            #  没存满
            node = FreqNode(key,value)   # 在缓存中新开一个空间节点
            self.map[key] = node
            node.freq=1
            self.size+=1

            # 将新节点放到链表中
            if node.freq not in self.dll_map:
                self.dll_map[node.freq]=DoubleLinkedList()

            self.dll_map[node.freq].push(node)

    def print(self):
        # 输出map和dll_map
        print(self.map)
        for k,dll in self.dll_map.items():
            print("Freq:%d" % k)
            print("DoubleLinkedList:")
            dll.print()
        print("\n")

def randTest(cache,times=10):   # 默认进行50次操作
    operate={"get":cache.get,"put":cache.put}
    key1 = list(range(1,10))
    key2 = list(range(1,6))
    for i in range(times):
        # print(operate.keys())
        op_name = random.choice(list(operate.keys()))
        op=operate[op_name]

        if op_name=="get":
            keyValue = random.choice(key2)
            print("Do %s(%s)" % (op_name,str(keyValue)))
            print(op(keyValue))
        else:
            keyValue = random.choice(key1)
            print("Do %s(%s,%s)" % (op_name,str(keyValue),str(keyValue)))
            op(keyValue,keyValue)



if __name__=="__main__":
    ram = {str(i):FreqNode(i,i) for i in range(1,6)}

    cache = LFUCache(capacity=3,ram=ram)

    # 随机插入和获取测试
    randTest(cache)
    # cache.get("5")
    # cache.put("2","2")
    # cache.get("1")
    # cache.put("2","2")
    # cache.put("6","6")
    # cache.put("1","1")
    cache.print()

# Do get(5)
# 5
# Do put(2,2)
# Do get(1)
# 1
# Do put(2,2)
# Do put(6,6)
# Do put(1,1)
# {'6': {6,6,1}, '1': {1,1,1}}
# Freq:1
# DoubleLinkedList:
# 共有3个节点，它们是：{2,2,1}->{6,6,1}->{1,1,1}
