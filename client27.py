#   client side
#   Author: Fraydi Goldstein

import socket
import protocol
import os
import filecmp

IP = "127.0.0.1"
# The path + filename where the copy of the screenshot at the client should be saved:
SAVED_PHOTO_LOCATION = r"C:\Users\Lenovo\Pictures\copy_screen.jpg"


def handle_server_response(my_socket, cmd):
    """
    Receive the response from the server and handle it, according to the request
    For example, DIR should result in printing the contents to the screen,
    Note- special attention should be given to SEND_PHOTO as it requires and extra receive
    """
    valid_msg, response = protocol.get_msg(my_socket)
    if valid_msg:
        list_cmd = cmd.split()
        if list_cmd[0] == 'DIR':
            print("The files in {} are: ".format(list_cmd[1]))
            print(response)
        if list_cmd[0] == 'DELETE':
            if not os.path.isfile(list_cmd[1]):
                print("Server response: ", response)
            else:
                print("The server didn't delete the file")
        if list_cmd[0] == 'COPY':
            if os.path.isfile(list_cmd[2]):
                if filecmp.cmp(list_cmd[1], list_cmd[2]):
                    print("Server response: ", response)
                else:
                    print("The server didn't copy the file")
            else:
                print("The server didn't copy the file")
        if list_cmd[0] == 'EXECUTE' or list_cmd[0] == 'TAKE_SCREENSHOT':
            print(response)
        if list_cmd[0] == 'SEND_PHOTO':
            count = 0
            size_file = int(response)
            with open(SAVED_PHOTO_LOCATION, 'ab') as hfile:
                while count < size_file:
                    packet = my_socket.recv(1024)
                    hfile.write(packet)
                    count += 1024
            print("The photo was sent and saved")
        elif list_cmd[0] == 'EXIT':
            print("The server response: ", response)
            print("Pls close your socket too")


def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # open socket with the server
    my_socket.connect((IP, protocol.PORT))
    # print instructions
    print('Welcome to remote computer application. Available commands are:\n')
    print('TAKE_SCREENSHOT\nSEND_PHOTO\nDIR\nDELETE\nCOPY\nEXECUTE\nEXIT')
    # loop until user requested to exit
    while True:
        cmd = input("Please enter command:\n")
        if protocol.check_cmd(cmd):
            packet = protocol.create_msg(cmd)
            my_socket.send(packet)
            handle_server_response(my_socket, cmd)
            if cmd == 'EXIT':
                break
        else:
            if cmd == 'EXIT':
                break
            print("Not a valid command, or missing parameters\n")

    print("Closing\n")
    my_socket.close()  # Close socket


if __name__ == '__main__':
    main()
