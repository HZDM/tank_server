import sys
import argparse


def args_process():
    parser = argparse.ArgumentParser(description='tank server.')
    parser.add_argument('port1', type=int,
                        help='port for player 1.')
    parser.add_argument('port2', type=int,
                        help='port for player 2.')
    parser.add_argument('mapfile',
                        help='map file to play.')
    return parser.parse_args()
    pass


def main():
    args = args_process()
    print(args)

    pass


if __name__ == "__main__":
    main()
    pass
