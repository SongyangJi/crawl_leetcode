# -*- coding: utf-8 -*-
# @Time : 2021/5/7
# @Author : Song yang Ji
# @File : BatchProcessing.py
# @Software: PyCharm


from multiprocessing import cpu_count
from multiprocessing import Process, Queue
from threading import Thread


class Runnable:
    """
    可执行任务类，覆盖run方法
    """

    def run(self):
        pass


class MyThread(Thread):
    def __init__(self, queue: Queue):
        """
        :param queue: 各个线程共享的任务队列
        """
        super().__init__()
        self.queue = queue

    def run(self) -> None:
        while True:
            try:
                r = self.queue.get(timeout=0.2)
                r.run()
            except:
                return


class MyProcess(Process):
    def __init__(self, threadNum, queue):
        """
        :param threadNum: 线程数
        :param queue: 任务队列
        """
        super().__init__()
        self.threadNum = threadNum
        self.queue = queue

    def run(self) -> None:
        # print(self.name, '启动')
        ts = []
        for i in range(self.threadNum):
            t = MyThread(self.queue)
            t.setName(self.name + '里的线程 ' + str(i))
            ts.append(t)
            t.start()
        for t in ts:
            t.join()


class TaskPool:
    def __init__(self, threadNum=4, processNum=cpu_count()):
        """
        :param threadNum: 线程数
        :param processNum: 进程数
        """
        self.threadNum = threadNum
        self.processNum = processNum
        self.queue = Queue()  # 各线程共享的队列

    def commit(self, runnable: Runnable):
        """
        提交任务，但不执行
        :param runnable: 可执行任务
        """
        self.queue.put(runnable)

    def batch(self):
        """
        开启多个进程，进行批处理任务
        """
        ps = []
        for i in range(self.processNum):
            p = MyProcess(self.threadNum, self.queue)
            p.name = '进程' + str(i)
            p.daemon = True
            ps.append(p)
            p.start()
        for p in ps:
            p.join()


class MyRun(Runnable):
    def __init__(self, name):
        self.name = name

    def run(self):
        with open(self.name, 'w') as f:
            for i in range(1000000):
                f.write(str(i) + '\n')
        pass


if __name__ == '__main__':
    import time

    begin = time.time()
    taskPool = TaskPool()
    for j in range(100):
        taskPool.commit(MyRun('dataset/' + str(j) + '.txt'))
    taskPool.batch()
    end = time.time()
    print('多进程+多线程 ：模拟写100个 1e6行的文本文件耗时', (end - begin), '秒')

    begin = time.time()
    for j in range(100):
        MyRun('dataset/' + str(j) + '.txt').run()
    end = time.time()
    print('串行 ： 模拟写100个 1e6行的文本文件耗时', (end - begin), '秒')

    # 模拟写100个 1e6行的文本文件耗时 3.2428581714630127 秒
    pass
