import sys
import argparse
import socket
import select
import queue
import copy


class sock_server(object):
    def __init__(self, port_list):
        self.servers = []

        for port in port_list:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setblocking(0)
            server.bind(('0.0.0.0', port))
            server.listen(1)
            self.servers.append(server)

        self.inputs = [self.servers[0], self.servers[1]]
        self.outputs = []
        self.recv_message_queues = {}
        self.send_message_queues = {}

    def start(self, func):
        inputs = self.inputs
        outputs = self.outputs
        recv_message_queues = self.recv_message_queues
        send_message_queues = self.send_message_queues

        try:
            while inputs:
                readable, writable, exceptional = select.select(inputs, outputs, inputs)

                for s in readable:
                    if s in self.servers:
                        connection, client_address = s.accept()
                        connection.setblocking(0)
                        inputs.append(connection)
                        recv_message_queues[connection] = queue.Queue()
                        send_message_queues[connection] = queue.Queue()
                    else:
                        data = s.recv(1024)
                        if data:
                            recv_message_queues[s].put(data)
                            if s not in outputs:
                                outputs.append(s)
                        else:
                            if s in outputs:
                                outputs.remove(s)
                            inputs.remove(s)
                            s.close()
                            del recv_message_queues[s]
                            del send_message_queues[s]

                for s in writable:
                    try:
                        next_msg = send_message_queues[s].get_nowait()
                    except queue.Empty:
                        outputs.remove(s)
                    else:
                        s.send(next_msg)

                for s in exceptional:
                    inputs.remove(s)
                    if s in outputs:
                        outputs.remove(s)
                    s.close()
                    del recv_message_queues[s]
                    del send_message_queues[s]

                func()

        except Exception as e:
            print(e)
            pass
        finally:
            all_opened_socket = set(self.inputs + self.outputs + self.servers)
            for s in all_opened_socket:
                print(s)
                s.close()


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


state = 0


def move_state(new_state):
    global state
    state = new_state


state_func = {
    'server_start': None,
    'wait_for_players': None,
    'game_start': None,
    'leg_start': None,
    'leg_end': None,
    'game_end': None
}


def main_process():
    if state_func[state]:
        state_func[state]()


def main():
    args = args_process()  # get arg by dicts
    print(args)

    ss = sock_server([args['port1'], args['port2']])

    move_state('server_start')
    ss.start(main_process)

    pass


if __name__ == "__main__":
    main()
    pass
