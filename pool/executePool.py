# -*- coding: utf-8 -*-
# @Time : 2021/5/7
# @Author : Song yang Ji
# @File : executePool.py
# @Software: PyCharm

from multiprocessing import cpu_count
from multiprocessing import Process, Queue
from threading import Thread



class Runnable():
    def run(self):
        pass


class MyThread(Thread):
    def __init__(self, queue: Queue):
        super().__init__()
        self.queue = queue

    def run(self) -> None:
        # print(self.getName(), '启动')
        while True:
            try:
                r = self.queue.get(timeout=0.1)
                r.run()
            except:
                return


class MyProcess(Process):
    def __init__(self, threads, processes, threads_list, queue):
        super().__init__()
        self.threads = threads
        self.processes = processes
        self.threads_list = threads_list
        self.queue = queue

    def run(self) -> None:
        # print(self.name, '启动')
        ts = []
        for i in range(self.threads):
            t = MyThread(self.queue)
            t.setName(self.name + '里的线程 ' + str(i))
            ts.append(t)
            t.start()
            self.threads_list.append(t)
        for t in ts:
            t.join()


class TaskPool:
    def __init__(self, threads=4, processes=cpu_count()):
        self.threads = threads
        self.processes = processes
        self.queue = Queue()
        self.threads_list = []

    def commit(self, runnable: Runnable):
        self.queue.put(runnable)

    def batch(self):
        ps = []
        for i in range(self.processes):
            p = MyProcess(self.threads, self.processes, self.threads_list, self.queue)
            p.name = '进程' + str(i)
            p.daemon = True
            ps.append(p)
            p.start()
        for p in ps:
            p.join()

