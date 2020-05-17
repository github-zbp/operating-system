# coding=utf-8

from threading import Lock,Condition

class ThreadSafeQueue:
    def __init__(self,max_size=0,timeout=None):
        self.queue=[]
        self.lock=Lock()
        self.cond = Condition()
        self.max_size = max_size
        self.timeout=timeout

    def size(self):
        self.lock.acquire()
        size = len(self.queue)
        self.lock.release()
        return size

    def put(self,item):
        self.cond.acquire()
        while self.max_size>0 and len(self.queue)>=self.max_size:
            res = self.cond.wait(timeout=self.timeout)  # True or False
            if not res:
                self.cond.release()     # 记得释放锁,否则其他线程会死锁
                return False

        self.queue.append(item)
        self.cond.notify()
        self.cond.release()

    def pop(self):
        self.cond.acquire()
        while len(self.queue)<=0:
            res = self.cond.wait(timeout=self.timeout)
            if not res:
                self.cond.release()
                return False

        item = self.queue.pop(0)
        self.cond.notify()
        self.cond.release()

        return item

    def batch_put(self,items):
        if not isinstance(items,list):
            items = list(items)

        for item in items:
            self.put(item)

    def get(self,index):
        self.lock.acquire()
        try:
            item = self.queue[index]
        except:
            item=None

        self.lock.release()
        return item


if __name__ == "__main__":
    from threading import Thread
    def producer(queue):
        for i in range(10000):
            queue.put(i)


    def consumer(queue):
        while True:
            print(queue.pop())
    queue = ThreadSafeQueue(max_size=100)
    t1 = Thread(target=producer,args=(queue,))
    t2 = Thread(target=producer,args=(queue,))
    t3 = Thread(target=consumer,args=(queue,))
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()