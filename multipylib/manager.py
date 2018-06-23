import time
import pickle
import multiprocessing
from multiprocessing.managers import SyncManager
from .common import QueueFinished
from .queues import RedisQueue


def results_handler(results_queue, report_queue):
    """
    This should run as a separate process. Its only job is to read the results
    queue (those comming from the worker node) and pass the results to the
    redis reults queue (so the runner can retrieve the results).

    Args:
        results_queue (Queue): A multiprocessing queue used to retrieve results
                               from node to manager process.
        report_queue (RedisQueue): Used to pass the incomming result from the
                                   manager to the runner.
    """
    # TODO It is possible that the report queue should be locked
    while True:
        result = results_queue.get()

        # TODO If worker puts None, then this would terminate!
        if isinstance(result, QueueFinished):
            return  # Terminate process safely

        report_queue.put(result)


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

    # TODO Shouldn't be possible to create Queues using the SyncManager.Queue?

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
    rq = RedisQueue(args.authkey, host=args.host, namespace='queue:results')

    # Fire a process/thread that is constantly fetching from the result queue
    # And sending it to the runner via another queue
    p = multiprocessing.Process(
        target=results_handler, args=(shared_result_queue, rq))
    p.start()

    try:
        while True:
            source_codes, kwargs = pickle.loads(q.get())
            for code in source_codes:
                shared_task_queue.put((code, kwargs))
    except KeyboardInterrupt:
        shared_task_queue.put(QueueFinished())
        shared_result_queue.put(QueueFinished())
        # send signal to nodes to stop (queue close? that also signals p)
        # send signal to stop process p
        time.sleep(3)  # Give time so that p gracefully quits (use join?)
        manager.shutdown()


def borrame(num):
    """
    This is a sample function task, this should be the function that has been
    read from the file.
    """
    return num * num
