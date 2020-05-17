# coding=utf-8

from threading import Lock,Condition,Event

class ThreadSafeQueue:
    def __init__(self,max_size=0,timeout=None):
        self.queue=[]
        self.lock=Lock()
        self.cond = Condition()
        self.max_size = max_size
        self.timeout=timeout
        # self.dismiss_flag = Event()
        # self.dismiss_flag.clear()       # 信号量默认为False,当解除pop或put的等待状态时设为true,用于防止唤醒后又去弹出或者添加元素

    def size(self):
        self.lock.acquire()
        size = len(self.queue)
        self.lock.release()
        return size

    # 用于解除pop或者put的等待状态并停止添加或弹出元素
    # def stopBlocking(self):
    #     self.cond.acquire()
    #     self.dismiss_flag.set()  # 修改信号量必须放在锁内进行以保证唤醒pop和修改信号量是一个原子操作;或者将修改信号量放在通知条件变量之前,这样不放在锁内也可以
    #     self.cond.notify()
    #     self.cond.release()


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