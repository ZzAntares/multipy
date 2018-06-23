import pickle
import traceback
from .queues import RedisQueue


def validate_file(file):
    """
    The compilation of the program is carried out,
    validating that it does not contain syntax errors

    Args:
        file (obj): File that content the program.

    Returns:
        result: The result for the compilation
    """
    try:
        # source file
        testContent = file.read()
        # generate a byte-code file from a source file
        compile(testContent, "<string>", 'exec')  # Used just for validation
        return testContent
    except Exception:
        print('==== Your code is not valid python3 code ====')
        traceback.print_exc()  # Print the error to the user
        return


def start(args):
    """
    This is the main function of this module. It uses the given args object to
    validate that the files compile.

    Args:
        args: This is the argparse.Namespace object holding command line
              arguments as attributes.
    """
    # Clean the argumets because some fields can't be easily serialized
    kwargs = vars(args).copy()
    del kwargs['file']
    del kwargs['func']

    validated = validate_file(args.file)

    if validated is None:
        # Will not send code that is not valid
        return

    q = RedisQueue(args.authkey, host=args.host)
    q.put(pickle.dumps((validated, kwargs)))  # Just send one code for now

    print('Files were sent to compile:', args.file.name)

    rq = RedisQueue(args.authkey, host=args.host, namespace='queue:results')
    result = rq.get()

    print('====== RESULT ======')
    print(result.decode(), '\n\n')
