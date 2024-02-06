# Landscape Mini Client

This is a mini-fied version of the Landscape Client. Minimally
compatible with minimal dependencies.

Intended to be used for testing.

Setup

    python3 -m venv ./venv
    . ./venv/bin/activate
    pip install -r ./requirements.txt

Register your client with a Landscape Server instance:

    python -m src.landscape_mini_client register \
        --account-name=standalone \
        --computer-title=mini-client \
        --server-host=localhost \
        --port=8080

Most calls default to HTTPS. If it hangs because of this, try with `--protocol=http --no-verify`.

Send a JSON-file as a message (after registration is accepted):

    python -m src.landscape_mini_client send_message --message=./my-message.json
