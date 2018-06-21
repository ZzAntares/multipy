import time
import multiprocessing
from multiprocessing.managers import SyncManager


def server_manager(host, port, authkey):
    task_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    class ServerManager(SyncManager):
        pass

    ServerManager.register('get_task_queue', callable=lambda: task_queue)
    ServerManager.register('get_result_queue', callable=lambda: result_queue)

    manager = ServerManager(address=(host, port), authkey=authkey)

    manager.start()
    print('Server started at {}:{}'.format(host, port))

    return manager


def start(args):
    manager = server_manager(args.host, args.port, args.authkey)
    shared_task_queue = manager.get_task_queue()
    shared_result_queue = manager.get_result_queue()

    # Get a reference to the function to process somehow
    # Pass the function reference, and its arguments in a pair
    shared_task_queue.put((borrame, {'num': 3}))

    # Wait for processing to finish
    threshold = 999  # A limit on tasks

    while threshold > 0:
        result = shared_result_queue.get()
        print('The result is: ', result)  # Give back results to runner somehow
        threshold -= 1

    time.sleep(2)
    manager.shutdown()


def borrame(num):
    """
    This is a sample function task, this should be the function that has been
    read from the file.
    """
    return num * num
