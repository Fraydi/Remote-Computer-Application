#  protocol

LENGTH_FIELD_SIZE = 4
PORT = 8820


def check_cmd(data):
    """
    Check if the command is defined in the protocol, including all parameters
    For example, DELETE c:\\work\\file.txt is good, but DELETE alone is not
    """
    list_data = data.split()
    if list_data[0] == 'TAKE_SCREENSHOT' or list_data[0] == 'EXIT' or list_data[0] == 'SEND_PHOTO':
        if int(len(list_data)) == 1:
            return True
        else:
            return False
    if list_data[0] == 'DIR' or list_data[0] == 'DELETE' or list_data[0] == 'EXECUTE':
        if int(len(list_data)) == 2:
            return True
        else:
            return False
    if list_data[0] == 'COPY':
        if int(len(list_data)) == 3:
            return True
        else:
            return False
    return False


def create_msg(data):
    """
    Create a valid protocol message, with length field
    """
    len_msg = str(len(data))
    zfill_len = len_msg.zfill(LENGTH_FIELD_SIZE)
    return (zfill_len + data).encode()


def get_msg(my_socket):
    """
    Extract message from protocol, without the length field
    If length field does not include a number, returns False, "Error"
    """
    try:
        len_mes = int(my_socket.recv(LENGTH_FIELD_SIZE).decode())
        data = my_socket.recv(len_mes).decode()
        return True, data
    except:
        return False, "Error"
