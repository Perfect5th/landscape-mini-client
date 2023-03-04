import textwrap

from craft_cli import BaseCommand, emit

from ..storage import ClientStorage


class ClearStorageCommand(BaseCommand):
    """Clears the local storage of this client."""

    name = "clear-storage"
    help_msg = "Clears this client's local storage."
    overview = textwrap.dedent("""
        Clear this client's local storage.

        Completely deletes any local state this client is maintaining,
        allowing it to start fresh.
    """)

    def run(self, _):
        storage = ClientStorage()

        storage.clear()
        emit.message("Local storage cleared")
