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
    try:
        # TODO It is possible that the report queue should be locked
        while True:
            result = results_queue.get()

            if isinstance(result, QueueFinished):
                return  # Terminate process safely

            report_queue.put(result)
    except KeyboardInterrupt:
        return


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
            code, params = pickle.loads(q.get())

            # Divide the task into multiple tasks for various nodes
            # Yield successive n-sized chunks from lst.
            def chunks(lst, n):
                for i in range(0, len(lst), n):
                    yield lst[i:i + n]

            chunksize = round(len(params) / args.workers_count)
            miniparams = list(chunks(params, chunksize))
            minitasks = zip([code] * len(miniparams), miniparams)

            for task in minitasks:
                shared_task_queue.put(task)
    except KeyboardInterrupt:
        print('Quitting...')
        time.sleep(2)  # Give time so that workers gracefully quits

    p.join()  # If result handler has not terminated wait for it
    manager.shutdown()  # Shutdown manager server
