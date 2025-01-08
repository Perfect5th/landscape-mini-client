import multiprocessing
import random
import sys
import time
import textwrap

import requests

from craft_cli import BaseCommand, emit


class PingspamCommand(BaseCommand):
    """Pings the Landscape Server instance as quickly as possible with
    insecure ID values drawn randomly from a provided pool.
    """

    name = "pingspam"
    help_msg = (
        "Pings the Landscape Server instance(s) as quickly as possible with"
        "insecure ID values drawn from a pool."
    )
    overview = textwrap.dedent(
        """
        Ping one or more Landscape Server instances as quickly as possible.

        For each Server provided, one is randomly selected and a ping is sent
        with a randomly-selected insecure ID from the list provided.
        """
    )

    def fill_parser(self, parser):
        parser.add_argument(
            "--servers",
            required=True,
            help="Path to a file containing a line-separated list of server"
            "FQDNs to which to send pings. These can contain ports."
        )
        parser.add_argument(
            "--insecure-ids",
            required=True,
            help="Path to a file containing a line-separated list of insecure"
            "IDs to use for pings."
        )
        parser.add_argument(
            "--workers",
            default=multiprocessing.cpu_count(),
            type=int,
            help="Number of workers to send pings with. Defaults to the number"
            "of CPUs reported by the machine."
        )

    def run(self, parsed_args):
        servers = []
        insecure_ids = []

        try:
            with open(parsed_args.servers) as servers_fp:
                servers.extend([s.strip() for s in servers_fp])

            with open(parsed_args.insecure_ids) as ids_fp:
                insecure_ids.extend([i.strip() for i in ids_fp])
        except OSError as err:
            print(err, file=sys.stderr)
            return

        # Validate the URLs
        emit.message("Starting pingspam...")

        pingspam(servers, insecure_ids, parsed_args.workers)


def pingspam(servers: list[str], insecure_ids: list[str], workers: int):
    """Spams ping requests at `servers`

    It does this by creating a multiprocessing pool of `workers` processes.
    """
    q = multiprocessing.Queue()

    processes = [multiprocessing.Process(target=pingloop, args=(servers, insecure_ids, q)) for _ in range(workers)]

    for p in processes:
        p.start()

    start_time = time.time()
    sent = 0
    while True:
        _ = q.get()
        sent += 1

        curr_time = time.time()
        diff = curr_time - start_time
        rate = int(sent // diff)

        emit.progress(f"Current rate: about {rate} pings/s. {sent} pings sent.")


def pingloop(servers: list[str], insecure_ids: list[str], q: multiprocessing.Queue):
    """Infinite loop sending pings, each time selecting a random `server` and
    `insecure_id`

    After each ping, puts a value on `q` to help indicate the ping rate.
    """
    while True:
        server = random.choice(servers)
        insecure_id = random.choice(insecure_ids)

        requests.get(
            f"http://{server}/ping?insecure_id={insecure_id}",
        )

        q.put(1)
