# N.B.: this is modified from the PRAW example
"""This example demonstrates the flow for retrieving a refresh token.

This tool can be used to conveniently create refresh tokens for later use with your web
application OAuth2 credentials.

To create a Reddit application visit the following link while logged into the account
you want to create a refresh token for: https://www.reddit.com/prefs/apps/

Create a "web app" with the redirect uri set to: http://localhost:8080

After the application is created, take note of:

- REDDIT_CLIENT_ID; the line just under "web app" in the upper left of the Reddit
  Application
- REDDIT_CLIENT_SECRET; the value to the right of "secret"

Usage:

    EXPORT praw_client_id=<REDDIT_CLIENT_ID>
    EXPORT praw_client_secret=<REDDIT_CLIENT_SECRET>
    python3 obtain_refresh_token.py

"""
import random
import socket
import sys
import os

import praw


def main():
    """Provide the program's entry point when directly executed."""
    with open('credentials.txt') as f:
        os.environ['praw_client_id'] = f.readline().strip()
        os.environ['praw_client_secret'] = f.readline().strip()
    scope_input = 'identity,read,submit'
    scopes = [scope.strip() for scope in scope_input.strip().split(",")]

    reddit = praw.Reddit(
        redirect_uri="http://localhost:8080",
        user_agent="obtain_refresh_token/v0 by u/bboe",
    )
    state = str(random.randint(0, 65000))
    url = reddit.auth.url(scopes, state, "permanent")
    print(f"Now open this url in your browser: {url}")

    client = receive_connection()
    data = client.recv(1024).decode("utf-8")
    param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
    params = {
        key: value for (key, value) in [token.split("=") for token in param_tokens]
    }

    if state != params["state"]:
        send_message(
            '400 Bad Request', client,
            f"State mismatch. Expected: {state} Received: {params['state']}",
        )
        return 1
    elif "error" in params:
        send_message('502 Bad Gateway', client, params["error"])
        return 1

    refresh_token = reddit.auth.authorize(params["code"])
    with open('credentials.txt', 'w') as f:
        f.write(os.environ['praw_client_id'] + '\n')
        f.write(os.environ['praw_client_secret'] + '\n')
        f.write(refresh_token + '\n')
    send_message('200 OK', client, f"Refresh token: {refresh_token}")
    return 0


def receive_connection():
    """Wait for and then return a connected socket..

    Opens a TCP connection on port 8080, and waits for a single client.

    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8080))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client


def send_message(status, client, message):
    """Send message to client and close the connection."""
    print(message)
    client.send(f"HTTP/1.1 {status}\r\n\r\n{message}".encode("utf-8"))
    client.close()


if __name__ == "__main__":
    sys.exit(main())
