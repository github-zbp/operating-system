# coding=utf-8

from threading import Thread
from ProcessThread import ProcessThread
from psutil import cpu_count
from Task import Task
from ThreadSafeQueue import ThreadSafeQueue

class ThreadPool:
    def __init__(self,pool_size=0):
        self.pool = []      # 线程池
        self.task_queue = ThreadSafeQueue()   # 大小没有限制的任务队列

        if pool_size==0:
            self.size = cpu_count()*2   # 定义线程池中线程的个数,默认CPU核数*2个线程
        else:
            self.size = pool_size

        for i in range(self.size):
            thread = ProcessThread(self.task_queue)
            self.pool.append(thread)

    # 运行线程
    def start(self):
        for thread in self.pool:
            thread.start()

    # 停止线程从队列取任务。当任务队列中的任务为0且不再增加时执行可以调用stop();当任务队列里面还有任务，但是不想线程继续获取任务时可调用stop(),虽然之后不会再取任务,但是线程会执行完当前正执行的任务再停止
    def stop(self):
        for thread in self.pool:
            thread.stop()

        while len(self.pool):
            thread = self.pool.pop()
            thread.join()   # 这一句是考虑到线程正在执行任务,等它执行完了再终止主线程

    def size(self):
        return len(self.pool)


    # 添加任务
    def put_task(self,task):
        if not isinstance(task,Task):
            raise TaskTypeException
        self.task_queue.put(task)

    # 批量添加任务
    def batch_put_task(self,tasks):
        self.task_queue.batch_put(tasks)


class TaskTypeException(Exception):
    pass


if __name__ == "__main__":
    from Task import AsyncTask
    import sys,os

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    # 测试有返回值的任务
    def asyncTask():
        num = 0
        for i in range(1000):
            num += i
        return num


    # 实例化一个线程池
    pool = ThreadPool()

    # 先将线程池中所有线程启动，一开始没有任务，所以所有线程启动之后立即进入等待状态
    pool.start()

    # 添加100000个任务给线程池，里面的线程会自动获取任务执行
    print("开始执行任务")
    task_list = []
    for i in range(100000):
        task = AsyncTask(asyncTask)
        pool.put_task(task)
        task_list.append(task)

    # 在此处可以进行一些主线程的逻辑处理，在主线程处理自己的逻辑的时候，线程池中的线程也在异步处理任务队列中的任务。

    for task in task_list:
        print(task.get_result())