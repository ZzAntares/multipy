import os
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from multiprocessing.managers import SyncManager
from .common import QueueFinished


def runner_task(data):
    bindings = {}
    code, param = data
    # TODO Return exist status of computation for better error handling
    try:
        exec(code, bindings)  # code was validated by the runner
        task = bindings['main']  # Extract the "main" function
        print('[WORKER #{}] Task is extracted and ready.'.format(os.getpid()))
        result = task(param)
        return {'args': param, 'result': result, 'success': True}
    except Exception as e:
        msg = "[WORKER] Got an error:\n\t{}\n\n{}".format(str(e), repr(e))
        return {'args': param, 'result': msg, 'success': False}


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

    try:
        with ProcessPoolExecutor(max_workers=args.procs) as pool:
            # TODO This could be refactored using a functional style
            #      A function that accepts the function that executes the pool
            while True:
                print('Waiting for tasks ...')
                data = task_queue.get()

                if isinstance(data, QueueFinished):  # Gracefuly quit process
                    task_queue.put(data)
                    print('Gracefuly quitting ...')
                    return

                code, params = data
                print('Got a new job! ...')

                # Divide the parameter list, so each process runs a piece
                chunksize = round(len(params) / args.procs)
                minitasks = zip([code] * len(params), params)

                # TODO Maybe it needs to convert from iterator to list
                task_results = list(
                    pool.map(runner_task, minitasks, chunksize=chunksize))

                result_queue.put(task_results)
                print('done!')

    # TODO Use signals instead? https://docs.python.org/3.6/library/signal.html
    # TODO Maybe this is not catched since is inside the pool
    except BrokenProcessPool:
        print('Process pool broke, a worker died and could not recover.')

    except EOFError:
        print('Connection closed, terminating...')  # Server was closed

    except KeyboardInterrupt:
        print('Quitting ...')
