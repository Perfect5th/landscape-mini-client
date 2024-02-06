import sys

from craft_cli import (
    ArgumentParsingError,
    CommandGroup,
    Dispatcher,
    EmitterMode,
    ProvideHelpException,
    emit,
)

from .commands.ping import PingCommand
from .commands.register import RegisterCommand
from .commands.send_message import SendMessageCommand
from .commands.storage import ClearStorageCommand


def main():
    emit.init(
        EmitterMode.BRIEF, "landscape-mini-client", "Starting landscape mini client."
    )

    command_groups = [
        CommandGroup("Register", [RegisterCommand]),
        CommandGroup("Exchange", [PingCommand, SendMessageCommand]),
        CommandGroup("Storage", [ClearStorageCommand]),
    ]

    summary = "Minimal subset of user-driven Landscape Client-Server" " interactions."
    dispatcher = Dispatcher("landscape-mini-client", command_groups, summary=summary)

    try:
        dispatcher.pre_parse_args(sys.argv[1:])
        dispatcher.load_command(None)
        dispatcher.run()
    except (ArgumentParsingError, ProvideHelpException) as err:
        print(err, file=sys.stderr)
        emit.ended_ok()
    else:
        emit.ended_ok()


if __name__ == "__main__":
    main()
