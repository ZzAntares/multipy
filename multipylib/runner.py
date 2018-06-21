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
        #source file
        testContent = file.read()
        # generate a byte-code file from a source file
        result = compile(testContent, "<string>", 'exec')
        return result
    except Exception:
        return

def start(args):
    """
    This is the main function of this module. It uses the given args object to
    validate that the files compile.

    Args:
        args: This is the argparse.Namespace object holding command line
              arguments as attributes.
    """
    args_files = iter(args.file)
    files_compiles = []
    #For each file, it is sent to validate
    for file in args_files:
        validated = validate_file(file)
        # just add the files you compile to the list
        if validated is not None:
            files_compiles.append(validated)

    print (files_compiles)
