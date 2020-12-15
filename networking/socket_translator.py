"""
To be launched by the Halite program as an intermediary,
in order to enable a pipe player to join.
"""
import traceback
import socket
import logging
import sys

try:
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_.bind(('', 65214))  # This is where the port is selected
    socket_.listen(2)
    connection, addr = socket_.accept()
    logging.warning(f"Connection accepted: {addr}")


    def send_string_pipe(to_be_sent):
        sys.stdout.write(to_be_sent + '\n')
        sys.stdout.flush()


    def get_string_pipe():
        str_pipe = sys.stdin.readline().rstrip('\n')
        logging.info(f"To std in got message: {str_pipe}")
        return str_pipe


    def send_string_socket(to_be_sent):
        to_be_sent += '\n'
        logging.info(f"To std in sending message: {to_be_sent}")
        connection.sendall(bytes(to_be_sent, 'ascii'))


    def get_string_socket():
        new_string = ""
        buffer = '\0'
        while True:
            buffer = connection.recv(1024).decode('ascii')
            if buffer != '\n':
                new_string += str(buffer)
            else:
                logging.warning(f"From std in got message: {new_string}")
                return new_string


    while True:

        send_string_socket(get_string_pipe())
        get_string_socket()  # from bot to stdout


        # get_string_socket()
        # Handle Init IO
        # send_string_socket(get_string_pipe())  # Player ID
        # send_string_socket(get_string_pipe())  # Map Dimensions
        # send_string_socket(get_string_pipe())  # Productions
        # send_string_socket(get_string_pipe())  # Starting Map
        # send_string_pipe(get_string_socket())  # Player Name / Ready Response

        # Run Frame Loop
        # while True:  # while True:
            # send_string_socket('Get map and play!')
            # send_string_socket(get_string_pipe())  # Frame Map
            # send_string_pipe(get_string_socket())  # Move List
        # send_string_socket('Stop playing!')

except ConnectionError as e:
    logging.warning(traceback.format_exc())
    pass