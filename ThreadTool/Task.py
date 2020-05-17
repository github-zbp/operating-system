# coding=utf-8

from uuid import uuid4
from threading import Condition

# 无返回值的任务
class Task:
    def __init__(self,func,*args,**kwargs):
        self.id = uuid4()
        self.callable = func    # 任务
        self.args = args
        self.kwargs = kwargs

    # 执行任务
    def call(self):
        res = self.callable(*self.args,**self.kwargs)
        return res

    def __str__(self):
        print("任务ID: %s" % str(self.id))

    def __repr__(self):
        print("任务ID: %s" % str(self.id))

# 有返回值的任务
class AsyncTask(Task):
    def __init__(self,func,*args,**kwargs):
        super(AsyncTask, self).__init__(func,*args,**kwargs)
        self.result = None
        self.cond = Condition()

    def set_result(self,result):
        self.cond.acquire()
        self.result=result
        self.cond.notify()
        self.cond.release()

    def get_result(self):
        if self.result is None:
            self.cond.acquire()
            self.cond.wait()
            self.cond.release()

        return self.result