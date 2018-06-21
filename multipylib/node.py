import multiprocessing
import queue
from multiprocessing.managers import SyncManager


def worker(task_queue, result_queue):
    """
    The worker function that runs until there are no more tasks to process,
    this reads the task queue, executes the retrieved function and places the
    result in the result queue.

    Args:
        task_queue: A shared multiprocessing.Queue where jobs to process are
                    placed by the server manager.
        result_queue: A shared multiprocessing.Queue where results of jobs are
                      placed, where will be read by the server manager.
    """
    # Run until task_queue is empty
    while True:
        try:
            task, kwargs = task_queue.get_nowait()
            task_result = task(**kwargs)  # Call function with its parameters
            result_queue.put(task_result)
        except queue.Empty:
            return


def connect_server(host, port, authkey):
    """
    Attempts to connect to a server manager listening in the specified host and
    port using the given authentication key and retrieve a connected server
    manager that is ready to accept tasks (non blocking).

    Args:
        host (str): Host where the server manager is listening for connections.
        post (int): Port where the server manager is listening for connections.
        authkey (str): Auth code used for joining as a new peer in the cluster.

    Returns:
        SyncManager: An instance of multiprocessing.managers.SyncManager that
                     is connected to a remote server manager that distributes
                     tasks over the connected nodes.
    """

    class ServerManager(SyncManager):
        pass

    ServerManager.register('get_task_queue')
    ServerManager.register('get_result_queue')

    manager = ServerManager(address=(host, port), authkey=authkey.encode())
    manager.connect()

    print('Client connected to {}:{}'.format(host, port))

    return manager


def start(args):
    """
    This is the main function of this module, it connects the current machine
    as a new processing node to the server manager specified in the arguments.

    Args:
        args: This is the argparse.Namespace object holding command line
              arguments as attributes.
    """
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

    # Wait for all workers to finish before terminating the main process
    for p in procs:
        p.join()
