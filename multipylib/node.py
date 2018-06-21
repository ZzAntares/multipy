import multiprocessing
import queue
from multiprocessing.managers import SyncManager


def worker(task_queue, result_queue):
    # Run until task_queue is empty
    while True:
        try:
            task, kwargs = task_queue.get_nowait()
            task_result = task(
                **kwargs)  # Call the function with its parameters
            result_queue.put(task_result)
        except queue.Empty:
            return


def connect_server(host, port, authkey):
    class ServerManager(SyncManager):
        pass

    ServerManager.register('get_task_queue')
    ServerManager.register('get_result_queue')

    manager = ServerManager(address=(host, port), authkey=authkey)
    manager.connect()

    print('Client connected to {}:{}'.format(host, port))

    return manager


def start(args):
    manager = connect_server(args.host, args.port, args.authkey)
    task_queue = manager.get_task_queue()
    result_queue = manager.get_result_queue()

    # Start to run a worker per process
    procs = []
    for _ in range(args.procs):
        p = multiprocessing.Process(
            target=worker, args=(task_queue, result_queue))
        procs.append(p)
        p.start()

    # Wait for all workers to finish before terminating main process
    for p in procs:
        p.join()
