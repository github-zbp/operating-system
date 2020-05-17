# coding=utf-8

from threading import Thread,Lock,Event
from Task import Task,AsyncTask

class ProcessThread(Thread):
    def __init__(self,queue,*args,**kwargs):
        super(ProcessThread, self).__init__(*args,**kwargs)
        self.queue = queue
        self.dismiss_flag=Event()
        self.args = args
        self.kwargs = kwargs


    def run(self):
        while True:
            if self.dismiss_flag.is_set():
                break
            task = self.queue.pop()
            if not isinstance(task,Task):
                continue
            result = task.call()

            # 执行完任务后,设置结果
            if isinstance(task, AsyncTask):
                task.set_result(result)

    def stop(self):
        print("线程停止获取任务")
        self.dismiss_flag.set()