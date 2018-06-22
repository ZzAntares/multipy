import pickle
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
        print('Your code is not valid python3 code')
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

    files_compiles = []
    # For each file, it is sent to validate
    for file in args.file:
        validated = validate_file(file)
        # just add the files you compile to the list
        if validated is not None:
            files_compiles.append(validated)

    q = RedisQueue(args.authkey, host=args.host)
    q.put(pickle.dumps((files_compiles, kwargs)))  # Just send one code for now

    print('Files were sent to compile:', files_compiles)
