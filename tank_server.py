import sys
import argparse
import socket
import select
import queue

class sock_server(object):
    def __init__(self, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(0)
        self.server.bind(('0.0.0.0', port))
        self.server.listen(5)
        self.inputs = [self.server]
        self.outputs = []
        self.message_queues = {}

    def start(self):
        inputs = self.inputs
        outputs = self.outputs
        message_queues = self.message_queues

        while inputs:
            readable, writable, exceptional = select.select(
                inputs, outputs, inputs)
            for s in readable:
                if s is self.server:
                    connection, client_address = s.accept()
                    connection.setblocking(0)
                    inputs.append(connection)
                    message_queues[connection] = queue.Queue()
                else:
                    data = s.recv(1024)
                    if data:
                        message_queues[s].put(data)
                        if s not in outputs:
                            outputs.append(s)
                    else:
                        if s in outputs:
                            outputs.remove(s)
                        inputs.remove(s)
                        s.close()
                        del message_queues[s]

            for s in writable:
                try:
                    next_msg = message_queues[s].get_nowait()
                except queue.Empty:
                    outputs.remove(s)
                else:
                    s.send(next_msg)

            for s in exceptional:
                inputs.remove(s)
                if s in outputs:
                    outputs.remove(s)
                s.close()
                del message_queues[s]




def args_process():
    parser = argparse.ArgumentParser(description='tank server.')
    parser.add_argument('port1', type=int,
                        help='port for player 1.')
    parser.add_argument('port2', type=int,
                        help='port for player 2.')
    parser.add_argument('mapfile',
                        help='map file to play.')
    args = vars(parser.parse_args())

    return args
    pass


def main():
    args = args_process() # get arg by dicts
    print(args)

    sock_server(25555)

    pass


if __name__ == "__main__":
    main()
    pass
