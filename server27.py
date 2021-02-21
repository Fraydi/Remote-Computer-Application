#   template - server side
#   Author: Fraydi Goldstein


import socket
import protocol
import glob
import os
import shutil
import subprocess
import pyautogui


IP = "0.0.0.0"
# The path + filename where the screenshot at the server should be saved:
PHOTO_PATH = r"C:\Users\Lenovo\Pictures\screen.jpg"


def check_client_request(cmd):
    """
    Break cmd to command and parameters
    Check if the command and params are good.
    For example, the filename to be copied actually exists
    Returns:
        valid: True/False
        command: The requested cmd (ex. "DIR")
        params: List of the cmd params (ex. ["c:\\cyber"])
    """
    # Use protocol.check_cmd first
    valid_cmd = protocol.check_cmd(cmd)
    # Then make sure the params are valid
    if valid_cmd:
        list_cmd = cmd.split()
        print()
        if int(len(list_cmd)) == 1:
            return True, list_cmd[0], [None]
        elif list_cmd[0] == 'DIR':
            if os.path.isdir(list_cmd[1]):
                return True, 'DIR', [r'{}'.format(list_cmd[1])]
            else:
                print("Directory isn't exist")
                return False, "Error", ["Error"]
        elif list_cmd[0] == 'EXECUTE':
            if os.path.exists(list_cmd[1]):
                siyomet = list_cmd[1].split('.')
                print(siyomet)
                if siyomet[1].lower() == 'exe':
                    return True, 'EXECUTE', [r'{}'.format(list_cmd[1])]
                else:
                    print("File isn't execute file")
                    return False, "Error", ["Error"]
            else:
                print("File isn't exist")
                return False, "Error", ["Error"]
        elif list_cmd[0] == 'SEND_PHOTO' or list_cmd[0] == 'DELETE':
            if os.path.isfile(list_cmd[1]):
                return True, list_cmd[0], [r'{}'.format(list_cmd[1])]
            else:
                print("File isn't exist")
                return False, "Error", ["Error"]
        elif list_cmd[0] == 'COPY':
            if os.path.isfile(list_cmd[1]):
                find_last_slash = list_cmd[2].rfind('\\')
                dir_file = list_cmd[2][0:find_last_slash:]
                print(dir_file)
                if os.path.isdir(dir_file):
                    return True, 'COPY', [r'{}'.format(list_cmd[1]), r'{}'.format(list_cmd[2])]
                else:
                    print("Directory isn't exist")
                    return False, "Error", ["Error"]
    else:
        return False, "Error", ["Error"]


def handle_client_request(command, params):
    """Create the response to the client, given the command is legal and params are OK
    For example, return the list of filenames in a directory
    Note: in case of SEND_PHOTO, only the length of the file will be sent
    Returns:
        response: the requested data
    """
    if command == 'DIR':
        files_list = glob.glob((params[0] + "\\*.*"))
        return '\n'.join(files_list)
    elif command == 'DELETE':
        os.remove(params[0])
        return "The file named {} was deleted".format(params[0])
    elif command == 'COPY':
        shutil.copy(params[0], params[1])
        return "The file {} was copied to {}".format(params[0], params[1])
    elif command == 'EXECUTE':
        subprocess.call(r'{}'.format(params[0]))
        return "The file {} was executed".format(params[0])
    elif command == 'TAKE_SCREENSHOT':
        image = pyautogui.screenshot()
        image.save(PHOTO_PATH)
        return "Screen shot was taken and saved to {}".format(PHOTO_PATH)
    elif command == 'SEND_PHOTO':
        return str(os.stat(PHOTO_PATH).st_size)
    elif command == 'EXIT':
        return "The connection was closed"
    else:
        return "Something went wrong"


def main():
    # open socket with client
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, protocol.PORT))
    server_socket.listen()
    print("Server is up and running")
    (client_socket, client_address) = server_socket.accept()
    print("Client connected")
    # handle requests until user asks to exit
    while True:
        # Check if protocol is OK, e.g. length field OK
        valid_protocol, cmd = protocol.get_msg(client_socket)
        if valid_protocol:
            # Check if params are good, e.g. correct number of params, file name exists
            valid_cmd, command, params = check_client_request(cmd)
            if valid_cmd:
                # prepare a response using "handle_client_request"
                response = handle_client_request(command, params)
                # add length field using "create_msg"
                valid_response = protocol.create_msg(response)
                # send to client
                client_socket.send(valid_response)
                if command == 'SEND_PHOTO':  # Send the data of the photo itself to the client
                    with open(PHOTO_PATH, 'rb') as hfile:
                        data = hfile.read()
                        client_socket.send(data)
                if command == 'EXIT':
                    break
            else:
                # prepare proper error to client
                response = 'Bad command or parameters'
                valid_response = protocol.create_msg(response)
                # send to client
                client_socket.send(valid_response)
        else:
            if cmd == 'EXIT':  # Handle EXIT command, no need to respond to the client
                break
            # prepare proper error to client
            response = 'Packet not according to protocol'
            valid_response = protocol.create_msg(response)
            # send to client
            client_socket.send(valid_response)
            # Attempt to clean garbage from socket
            client_socket.recv(1024)
    print("Closing connection")
    server_socket.close()  # Close sockets
    client_socket.close()


if __name__ == '__main__':
    main()
