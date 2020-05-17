# coding=utf-8

from DoubleLinkedList import DoubleLinkedList,Node

class LRUCache:
    def __init__(self,capacity,ram):
        self.ram=ram    # 模拟内存，里面放的是Node节点
        self.capacity = capacity
        self.size=0
        self.map={}     # 模拟缓存，里面放的是Node节点
        self.dll=DoubleLinkedList()     # 双向链表

    def get(self,key):
        key = str(key)
        node = self.map.get(key,self.__getFromRam(key))   # 缓存中有就从缓存取，否则从内存取
        if node:
            return node.value
        else:
            return False

    def put(self,key,value):
        key=str(key)
        if key not in self.map:     # 缓存中没有这个空间的地址，则为新增
            # 分两种情况，缓存满了和缓存没满
            if self.size >= self.capacity:  # 满了
                old_node=self.dll.pop()      # 从链表尾部弹出尾部节点
                self.map.pop(old_node.key)   # 发生置换，从缓存中删除该旧节点
                self.size-=1

                # 从缓存链表中弹出的数据应该置换（写入）到主存中
                self.ram[old_node.key]=old_node

            # 没满则不作额外操作
            node = Node(key,value)
            self.map[key]=node
            self.dll.unshift(node)
            self.size+=1
        else:   # 修改
            self.dll.remove(self.map[key])  # 将该节点放到链表头部
            self.dll.unshift(self.map[key])
            self.map[key]=value     # 修改该节点的值




    def __getFromRam(self,key):
        # key=str(key)
        if key not in self.ram:
            return False

        node = self.ram[key]
        self.put(key,node.value)


    def print(self):
        self.dll.print()
        print(self.map)
        print(self.ram)
        print("\n")

if __name__=="__main__":
    ram = {str(i):Node(i,i) for i in range(1,21)}  # 定义内存
    
    # 定义缓存
    cache=LRUCache(capacity=3,ram=ram)

    # CPU往缓存中写入数据
    cache.put(33,33)
    cache.put(100,100)
    cache.put(2,2)  # 主存置换到缓存的数据
    cache.print()

    cache.get(10)
    cache.get(1000)
    cache.put(4,6)  # 修改key为4的地址空间的数据值为6
    cache.print()

    cache.put(22,22)
    cache.get(33)
    cache.get(100)
    cache.print()