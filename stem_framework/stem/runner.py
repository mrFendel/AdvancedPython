import threading
import time
import warnings
import asyncio
from multiprocessing import Process

asyncio.set_event_loop(asyncio.new_event_loop())


class ThreadingRunner(threading.Thread):
    def __init__(self, MAX_WORKERS):
        self.func_list = []
        self.args_list = []
        self.MAX_WORKERS = MAX_WORKERS
        self.threads = []

    def add_func(self, func, args):
        if len(self.func_list) < self.MAX_WORKERS:
            self.func_list.append(func)
            self.args_list.append(args)
        else:
            warnings.warn(f'Number of functions is more than MAX_WORKERS = {self.MAX_WORKERS}.')

    def get_treads(self):
        return tuple(self.threads)

    def thread_run(self):
        for i in range(len(self.func_list)):
            f = self.func_list[i]
            args = self.args_list[i]
            t = threading.Thread(target=f, args=args)
            self.threads.append(t)
            t.start()
        for t in self.threads:
            t.join()


class AsyncRunner():
    def __init__(self):
        self.func_list = []
        self.args_list = []
        self.tasks_list = []
        self.loop = asyncio.get_event_loop()

    def async_run(self):
        # try:
        t = time.time()
        self.loop.run_until_complete(self.async_main())
        self.loop.close()
        print(time.time() - t)
        # except :
        #     pass

    def add_func(self, func, args):
        self.func_list.append(func)
        self.args_list.append(args)

    def get_treads(self):
        return tuple(self.threads)

    async def async_main(self):
        loop = self.loop
        for i in range(len(self.func_list)):
            f = self.func_list[i]
            args = self.args_list[i]
            self.tasks_list.append(loop.create_task(f(args[0])))
        await asyncio.wait(self.tasks_list)


class ProcessingRunner(Process):
    def __init__(self, MAX_WORKERS):
        self.func_list = []
        self.args_list = []
        self.MAX_WORKERS = MAX_WORKERS
        self.processes = []

    def add_func(self, func, args):
        if len(self.func_list) < self.MAX_WORKERS:
            self.func_list.append(func)
            self.args_list.append(args)
        else:
            warnings.warn(f'Number of functions is more than MAX_WORKERS = {self.MAX_WORKERS}.')

    def get_treads(self):
        return tuple(self.processes)

    def thread_run(self):
        for i in range(len(self.func_list)):
            f = self.func_list[i]
            args = self.args_list[i]
            p = Process(target=f, args=args)
            self.processes.append(p)
            p.start()
        for p in self.processes:
            p.join()
