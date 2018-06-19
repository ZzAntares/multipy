#!/usr/bin/env python3
import os
from multipy import node, runner, manager

# Se usan si no se especifican otras en la linea de comandos
MULTIPY_HOST = os.getenv('MULTIPY_HOST', '127.0.0.1')
MULTIPY_PORT = os.getenv('MULTIPY_PORT', '3000')

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process tasks in cluster')
    parser.add_argument('--host', dest='host', help='Manager address')
    parser.add_argument('--port', dest='port', help='Manager port')
    parser.set_defaults(host=MULTIPY_HOST, port=MULTIPY_PORT)

    # Allowing subcommands
    subparsers = parser.add_subparsers(
        title='Subcommands',
        description='Mode of execution of multipy',
        help='are valid subcommands')

    # node parser
    parser_node = subparsers.add_parser('node')
    parser_node.set_defaults(func=node.start)

    # node parser
    parser_manager = subparsers.add_parser('manager')
    parser_manager.set_defaults(func=manager.start)

    # node parser
    parser_run = subparsers.add_parser('run')
    parser_run.add_argument(
        'file',
        nargs='+',
        type=argparse.FileType('r'),
        help='Python file with main() to execute')
    parser_run.set_defaults(func=runner.start)

    # dispatch subcommands
    args = parser.parse_args()
    args.func(args)
