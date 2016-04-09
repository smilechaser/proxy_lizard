# proxy_lizard
"Man-in-the-middle" logging proxy for raw TCP/IP socket data.

# Background #
I wanted a tool to help me log the interaction of packets between a MineCraft client and server.

There's an old snippet named "pinhole.py" still floating around on the internet that does something similar but I wanted to see what I could do with python3.

# Details #
**Status:** Experimental *(use at your own risk)*

**Developed on:**

- Python3
- OSX 10.11.4 (El Capitan)

Although I imagine it should work on any *nix-like O/S with python3.

**License:** The MIT License

# Installation #
No installation necessary. Just copy the file *proxy_lizard.py* somewhere and run it! 😉

# Usage #

For usage instructions and additional options:

`python3 proxy_lizard.py --help`

Basic usage:

`python3 --to localhost:25565`

This will start a TCP/IP server listening on `localhost` and a random port. When a client connects the server will:

1. connect to `localhost` on port 25565
2. log all sent/received data to a file named packet_dump_XXX.dat, where XXX is an ISO formatted timestamp
3. continue until either side disconnects


