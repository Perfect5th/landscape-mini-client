#!/usr/bin/env python3

import argparse
import logging
import sys
import warnings

from commands.register import register


def main(args):
    warnings.filterwarnings("ignore", message="unverified https")

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(prog="landscape_mini_client")
    subparsers = parser.add_subparsers()

    parser_register = subparsers.add_parser("register", help="register help")
    parser_register.set_defaults(func=register)
    parser_register.add_argument("--account-name", required=True)
    parser_register.add_argument("--computer-title", required=True)
    parser_register.add_argument("--server-host", required=True)
    parser_register.add_argument("--registration-key", default="")
    parser_register.add_argument("--tags", default="")
    parser_register.add_argument("--container-info", default="")
    parser_register.add_argument("--vm-info", default="")

    results = parser.parse_args(args)

    results.func(results)


if __name__ == "__main__":
    main(sys.argv[1:])
