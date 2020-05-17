# coding=utf-8

from DoubleLinkedList import DoubleLinkedList,Node

# 模拟FIFO缓存置换算法
class FIFOCache:
    def __init__(self,capacity,ram):    # capacity是链表中的容量，也是缓存中的容量，例如 capacity=10，表示缓存只能容纳10个空间，链表只能最多有10个节点
        self.ram = ram  # 模拟主存，内含有多个空间，每个小空间放着一个key-value数据，ram有多个key，key是存储空间在主存中的地址，ram的值是node节点
        self.map={}     # map模拟高速缓存,map有多个key，key是存储空间在缓存中的地址,map中的值是node节点,故map放的是地址和节点的映射，ram也是
        self.size=0     # size是缓存中的空间个数
        self.capacity=capacity  # 缓存空间的最大个数，也是双向链表的最大节点数
        self.doubleLinkedList = DoubleLinkedList()  # 双向链表，用来记录map中数据空间的顺序，在map中的数据也一定会在双向链表中有对应节点

    # 模拟CPU从高速缓存中获取数据
    def get(self,key):  # 根据地址获取空间内的数据
        key = str(key)
        node = self.map.get(key,self.__getFromRam(key))  # CPU根据数据的地址从缓存中找这个数据，如果缓存中没有则从内存中找
        if node:
            return node.value
        else:   # 该情况是当从主存中取数据，但主存也没有该数据的情况。CPU是不会犯这种错误的，人会
            return False

    def __getFromRam(self,key):
        key=str(key)

        # 如果主存中没有数据则返回False
        if key not in self.ram:
            return False

        # 如果主存中有数据，则将数据写入缓存中，然后返回数据给CPU。这里分为两种情况：缓存还没写满和缓存写满了
        node = self.ram.get(key)
        self.put(node.key,node.value)

        return node

    # CPU或者主存将数据写入或者更新缓存
    def put(self,key,value):
        key = str(key)
        newNode = Node(key,value)
        if key in self.map: # 如果缓存中已有这个地址的数据，说明是更新
            node = self.map[key]
            self.doubleLinkedList.remove(node)
            self.doubleLinkedList.push(newNode)
            self.map[key]=newNode
        else:   # 新增
            if self.size==self.capacity:    # 如果缓存写满了,则进行先进先出置换
                node = self.doubleLinkedList.shift()    # 获取弹出的节点，待会要从map中删除这个节点
                # print(node.key)
                del(self.map[node.key])
                self.size-=1

                # 将弹出来的节点写一份到内存中
                if node.key not in self.ram:
                    self.ram[node.key] = node

            self.doubleLinkedList.push(newNode)
            self.map[key]=newNode
            self.size+=1

    def print(self):
        self.doubleLinkedList.print()
        print(self.map)
        print(self.ram)
        print("\n")


if __name__=="__main__":
    ram={str(i):Node(key=i,value=i) for i in range(1,21)}    # 定义已占用的内存空间和每个内存空间的数据，key是地址，value是数据

    # 假设一个缓存有3个空间
    cache = FIFOCache(capacity=3,ram=ram)

    # 在类外put的都是CPU写入缓存的数据，而在__getFromRam方法put的都是从主存置换到缓存的数据
    cache.put(25,25)        # key大于20的都是内存中不存在的，说明是CPU运算产生的数据写入了缓存
    cache.put(12,12)
    cache.put(100,100)
    cache.print()
    cache.put(50,50)
    cache.print()
    print(cache.get(10))
    print(cache.get(5))
    print(cache.get(2))
    print(cache.get(100))
    cache.print()
