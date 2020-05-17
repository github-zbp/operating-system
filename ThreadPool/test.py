# coding=utf-8
# import sys,os
#
# print(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# os.chdir(".")

from Task import Task
from ThreadPool import ThreadPool
from Task import AsyncTask,Task


# 测试有返回值的任务
def asyncTask():
    num = 0
    for i in range(1000):
        num += i
    return num

def commonTask():
    num = 0
    for i in range(1000):
        num += i
    print(num)

# 实例化一个线程池
pool = ThreadPool()

# 先将线程池中所有线程启动，一开始没有任务，所以所有线程启动之后立即进入等待状态
pool.start()

# 添加100000个任务给线程池，里面的线程会自动获取任务执行
print("开始执行任务")
task_list = []
for i in range(100000):
    task = Task(commonTask)
    # task = AsyncTask(asyncTask)
    pool.put_task(task)
    task_list.append(task)

# 在此处可以进行一些主线程的逻辑处理，在主线程处理自己的逻辑的时候，线程池中的线程也在异步处理任务队列中的任务。

for task in task_list:
    print(task.get_result())