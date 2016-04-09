'''
"Man-in-the-middle" logging proxy for raw TCP/IP socket data.

Based on code from: https://docs.python.org/3.5/library/socketserver.html

Use only for good...and not for anything mission critical...
'''

import sys
import argparse
import socket
import threading
import socketserver
import datetime


class RequestHandler(socketserver.BaseRequestHandler):

    def setup(self):

        # this is our connection to the "real server"
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.server.target_addr, self.server.target_port))

        self.to_client_buffer = b''
        self.to_server_buffer = b''

        now = datetime.datetime.now()

        filename_template = self.server.filename_template

        # here are the available "choices" for use in the filename template
        #   i.e. 'my_filename_{isonow}.dat'
        filename_data = {
            'isonow': now.isoformat().replace('-', '_').replace(':', '_')
        }

        filename = filename_template.format(**filename_data)

        print('Logging to: {}'.format(filename))

        self.outfile = open(filename, 'w')

    def handle(self):

        self.client.setblocking(False)
        self.request.setblocking(False)

        try:

            while True:

                while True:

                    data = None

                    try:
                        data = self.request.recv(1024)
                    except BlockingIOError:
                        pass

                    if data is None or data == b'':
                        break

                    self.outfile.write('\n-->')
                    self.outfile.write(str(data))

                    self.to_client_buffer = self.to_client_buffer + data

                    break

                while True:

                    data = None

                    try:
                        data = self.client.recv(1024)
                    except BlockingIOError:
                        pass

                    if data is None or data == b'':
                        break

                    self.outfile.write('\n<--')
                    self.outfile.write(str(data))

                    self.to_server_buffer = self.to_server_buffer + data

                    break

                self.to_server_buffer = self.send_buffer(self.request,
                                                         self.to_server_buffer)

                self.to_client_buffer = self.send_buffer(self.client,
                                                         self.to_client_buffer)
        except ConnectionResetError:
            pass

    def finish(self):

        self.client.close()

        self.outfile.close()

    def send_buffer(self, con, buffer):

        bytes_to_send = len(buffer)

        while bytes_to_send > 0:

            try:
                bytes_sent = con.send(buffer)
            except BlockingIOError:
                return buffer

            buffer = buffer[bytes_sent:]

            bytes_to_send -= bytes_sent

        return b''


class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def main():

    parser = argparse.ArgumentParser(
        argument_default=argparse.SUPPRESS,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--listen-addr', default='localhost',
                        help='address to listen on')
    parser.add_argument('--listen-port', type=int, default=0,
                        help='port to listen on')
    parser.add_argument('--to-port', type=int,
                        help='our "real server" port')
    parser.add_argument('--to-addr',
                        help='our "real server" address')
    parser.add_argument('--to',
                        help='our "real server" address[:port]')
    parser.add_argument('--filename-template',
                        default='packet_dump_{isonow}.dat',
                        help='filename (templatized) to use for log filename')

    args = parser.parse_args()

    listen_addr = args.listen_addr
    listen_port = args.listen_port
    to_addr = None
    to_port = None
    filename_template = args.filename_template

    if 'to' in args:

        to_addr, to_port = (args.to.split(':', 1) + [None])[0:2]
        to_port = int(to_port)

    else:

        if 'to_addr' in args:
            to_addr = args.to_addr

        if 'to_port' in args:
            to_port = int(args.to_port)

    if not (to_addr and to_port):
        print('you must specify a target address and port')
        sys.exit()

    if not listen_addr:
        print('you must specify an address/hostname to listen on')
        sys.exit()

    server = Server((listen_addr, listen_port), RequestHandler)
    server.target_addr = to_addr
    server.target_port = to_port
    server.filename_template = filename_template

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    ip, port = server.server_address
    print("Server loop running {}:{}".format(ip, port))

    server.serve_forever()

if __name__ == "__main__":

    main()
