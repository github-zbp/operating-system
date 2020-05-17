# coding=utf-8

# 节点类
class Node:
    def __init__(self,key,value):
        self.key = str(key)
        self.value=str(value)
        self.prev=None      # 节点的向前指针，默认指向空
        self.next=None      # 节点的向后指针，默认指向空

    def __str__(self):
        return "{%s,%s}" % (self.key,self.value)

    def __repr__(self):
        return "{%s,%s}" % (self.key,self.value)


# 双向链表类
class DoubleLinkedList:
    def __init__(self,capacity=0xffff):
        self.capacity = capacity    # 定义链表的容量，默认为2^16-1=65535个节点
        self.head=None      # 链表的头部指针，一开始链表中没有节点，所以为空
        self.tail=None      # 链表的尾部指针，一开始链表中没有节点，所以为空
        self.size=0         # 节点个数

    # 往头部添加节点
    def unshift(self,node):
        if not self.head:   # 如果头部指针为空，说明链表没有节点，此时头部指针和尾部指针都指向新加的节点
            self.head=node
            self.tail=node
            node.prev=None
            node.next=None
        else:   # 如果链表已有节点，则把头部指针指向新添节点node，node向后指针指向原头部节点，原头部节点的向前指针指向node
            node.prev=None
            node.next=self.head
            self.head.prev=node
            self.head=node      #头部指针指向node节点

        self.size+=1        # 节点数+1

    # 往头部弹出节点
    def shift(self):
        if not self.head:   # 如果链表没有节点，则返回空
            return

        node = self.head
        if self.size==1:    # 如果链表只有一个节点
            self.head=None
            self.tail=None
        else:
            # 将原头部节点的向后指针指向空，将头部指针指向原头部节点的下一个节点,将新头部节点的向前指针指向空
            self.head=self.head.next    # 将头部指针指向原头部节点的下一个节点
            node.next=None      # 将原头部节点的向后指针指向空
            self.head.prev=None # 将新头部节点的向前指针指向空

        self.size-=1

        return node     # 返回被弹出的节点

    # 往尾部添加节点
    def push(self,node):
        if not self.tail:
            self.head=node
            self.tail=node
            node.prev=None
            node.next=None
        else:
            node.next=None
            self.tail.next = node   # 原尾部节点的向后指针指向node
            node.prev=self.tail     # node的向前指针指向原尾部节点
            self.tail=node          # 链表的尾部指针指向node

        self.size+=1

    # 往尾部弹出节点
    def pop(self):
        if not self.tail:
            return

        node=self.tail
        if self.size==1:
            self.tail=None
            self.head=None
        else:
            node.prev.next=None     # 原尾部节点的上一个节点的尾部指针指向空
            self.tail=node.prev     # 尾部指针指向原尾部节点的上一个节点
            node.prev=None          # 原尾部节点的向前指针指向空

        self.size-=1
        return node



    # 从任意位置删除节点
    def remove(self,node):
        if node==self.head: # 如果删除的节点是头部节点，则调用shift
            return self.shift()
        elif node==self.tail:
            return self.pop()
        else:   # 如果不是头部节点也不是尾部节点
            prev = node.prev
            next = node.next

            if not prev or not node.next:   # 如果要删除的节点没有前后节点，而且也不是头部或者尾部节点，那么说明该节点不在链表中
                return
            node.prev=None
            node.next=None
            prev.next=next
            next.prev=prev

            self.size-=1
            return node

    # 输出链表所有节点
    def print(self):
        current = self.head  # 把当前指针指向头部节点
        content=""
        while current:
            content+=str(current)
            if current.next:
                content+="->"
            current=current.next

        print("共有%d个节点，它们是：%s" % (self.size,content))


if __name__=="__main__":
    l=DoubleLinkedList()
    node_box = []
    for i in range(1,11):    # 创建10个节点
        node_box.append(Node(i,i))

    l.unshift(node_box[0])
    l.push(node_box[1])
    l.push(node_box[3])
    l.print()

    l.shift()
    l.unshift(node_box[8])
    l.pop()
    l.push(node_box[5])
    l.print()

    l.unshift(node_box[3])
    l.push(node_box[0])
    l.print()

    l.remove(node_box[0])
    l.remove(node_box[1])
    l.remove(node_box[7])
    l.print()