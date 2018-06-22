import time
import pickle
import multiprocessing
from multiprocessing.managers import SyncManager
from .queues import RedisQueue


def server_manager(host, port, authkey):
    """
    This starts a server manager in the background (non blocking) that listens
    for connections in the specified host, port and establishes
    authentification using the provided authentification key.

    Args:
        host (str): Host to bind the server manager to.
        post (int): Port to bind the server manager.
        authkey (str): Auth code used for accepting new peers in the cluster.

    Returns:
        SyncManager: An instance of multiprocessing.managers.SyncManager that
                     distributes tasks over the connected nodes.
    """
    # TODO Can most of this function be replaced with mutliprocessing.Manager?
    task_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    class ServerManager(SyncManager):
        pass

    ServerManager.register('get_task_queue', callable=lambda: task_queue)
    ServerManager.register('get_result_queue', callable=lambda: result_queue)

    manager = ServerManager(address=(host, port), authkey=authkey.encode())

    manager.start()
    print('Server started at {}:{}'.format(host, port))

    return manager


def start(args):
    """
    This is the main function of this module. It uses the given args object to
    start a server manager that handles the distributed computing cluster.

    Args:
        args: This is the argparse.Namespace object holding command line
              arguments as attributes.
    """
    manager = server_manager(args.host, args.port, args.authkey)
    shared_task_queue = manager.get_task_queue()
    shared_result_queue = manager.get_result_queue()

    # Get a reference to the function to process somehow
    q = RedisQueue(args.authkey, host=args.host)
    source_codes, kwargs = pickle.loads(q.get())
    for code in source_codes:
        shared_task_queue.put((code, kwargs))

    # TODO Instead of task limit one could use Queue's task_done() and join()?
    # Wait for processing to finish
    threshold = args.task_limit  # A limit on tasks

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
