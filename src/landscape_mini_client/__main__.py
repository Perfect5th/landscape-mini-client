import argparse
import logging
import sys

from .commands.register import register


def main():
    args = sys.argv[1:]

    parser = argparse.ArgumentParser(prog="landscape_mini_client")
    parser.add_argument("--debug", action="store_true",
                        help="print debug logs")
    subparsers = parser.add_subparsers()

    parser_register = subparsers.add_parser(
        "register", help="register with a Landscape Server instance")
    parser_register.set_defaults(func=register)
    parser_register.add_argument("--account-name", required=True)
    parser_register.add_argument("--computer-title", required=True)
    parser_register.add_argument("--server-host", required=True)
    parser_register.add_argument("--registration-key", default="")
    parser_register.add_argument("--tags", default="")
    parser_register.add_argument("--container-info", default="")
    parser_register.add_argument("--vm-info", default="")
    parser_register.add_argument("--protocol", default="https")
    parser_register.add_argument("--port", default=443)
    parser_register.add_argument(
        "--no-verify", action="store_false", dest="verify",
        help="Do not verify SSL/TLS")

    results = parser.parse_args(args)

    logging.basicConfig(level=logging.DEBUG if results.debug else logging.INFO)

    if hasattr(results, "func"):
        results.func(results)
    else:
        parser.print_usage()


if __name__ == "__main__":
    main()
