"""
{{MODIFIED - MAY BREAK}}
- CS2911 - 0NN
- Fall 2017
- Lab N
- Names:
 -
 -

A simple TCP server/client pair.

The application protocol is a simple format: For each file uploaded, the client first sends four (big-endian) bytes indicating the number of lines as an unsigned binary number.

The client then sends each of the lines, terminated only by '\\n' (an ASCII LF byte).

The server responds with 'A' if it accepts the file, and 'R' if it rejects it.

Then the client can send the next file.
"""

# import the 'socket' module -- not using 'from socket import *' in order to selectively use items with 'socket.' prefix
import socket
import struct
import time
import sys

# Port number definitions
# (May have to be adjusted if they collide with ports in use by other programs/services.)
TCP_PORT = 12222

# Address to listen on when acting as server.
# The address '' means accept any connection for our 'receive' port from any network interface
# on this system (including 'localhost' loopback connection).
LISTEN_ON_INTERFACE = ''

# Address of the 'other' ('server') host that should be connected to for 'send' operations.
# When connecting on one system, use 'localhost'
# When 'sending' to another system, use its IP address (or DNS name if it has one)
# OTHER_HOST = '155.92.x.x'
OTHER_HOST = 'localhost'


def main():
    """
    Allows user to either send or receive bytes
    """
    # Get chosen operation from the user.
    action = input('Select "(1-TS) tcpsend", or "(2-TR) tcpreceive":')
    # Execute the chosen operation.
    if action in ['1', 'TS', 'ts', 'tcpsend']:
        tcp_send(OTHER_HOST, TCP_PORT)
    elif action in ['2', 'TR', 'tr', 'tcpreceive']:
        tcp_receive(TCP_PORT)
    else:
        print('Unknown action: "{0}"'.format(action))


def tcp_send(server_host, server_port):
    """
    - Send multiple messages over a TCP connection to a designated host/port
    - Receive a one-character response from the 'server'
    - Print the received response
    - Close the socket

    :param str server_host: name of the server host machine
    :param int server_port: port number on server to send to
    """
    print('tcp_send: dst_host="{0}", dst_port={1}'.format(server_host, server_port))
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((server_host, server_port))

    while (1):  # For sending data multiple times
        num_lines = int(input('Enter the number of lines you want to send (0 to exit):'))
        tcp_socket.sendall(b'\x00\x00')
        time.sleep(1)
        tcp_socket.sendall(b'\x00' + bytes((num_lines,)))
        print('Now enter all the lines of your message')

        # This client code does not completely conform to the specification.
        #
        # In it, I only pack one byte of the range, limiting the number of lines this
        # client can send.
        #
        # While writing tcp_receive, you will need to use a different approach to unpack to meet the specification.
        #
        # Feel free to upgrade this code to handle a higher number of lines, too.


        # Enter the lines of the message. Each line will be sent as it is entered.
        for line_num in range(0, num_lines):
            line = input('')
            tcp_socket.sendall(line.encode('utf-8') + b'\n')

        print('Done sending. Awaiting reply.')
        response = tcp_socket.recv(1)
        print(response)
        if response == b'A':  # Note: == in Python is like .equals in Java
            print('File accepted.')
        elif response == b'Q':  # Reminder: == in Python is like .equals in Java
            # If response is Q then connection should be terminated.
            print('Server closing connection, as expected.')
            tcp_socket.close()
            break;
        else:
            print('Unexpected response:', response)


def tcp_receive(listen_port):
    """
    - Listen for a TCP connection on a designated "listening" port
    - Accept the connection, creating a connection socket
    - Print the address and port of the sender
    - Repeat until a zero-length message is received:
      - Receive a message, saving it to a text-file (1.txt for first file, 2.txt for second file, etc.)
      - Send a single-character response 'A' to indicate that the upload was accepted.
    - Send a 'Q' to indicate a zero-length message was received.
    - Close data connection.

    :param int listen_port: Port number on the server to listen on
    """
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind((LISTEN_ON_INTERFACE, listen_port))
    listen_socket.listen(1)  # Num of conn. to accept
    data_socket, sender_address = listen_socket.accept()
    file_number = 0


    print('tcp_receive (server): listen_port={0}'.format(listen_port))
    numline = read_header(data_socket)
    while (numline):  # Loop until number of lines received is 0
        file_text = ""
        message = read_message(numline, data_socket)
        file_text += str(message.decode())  # Creating string to be saved to file
        data_socket.send(b'A')
        numline = read_header(data_socket)
        file_number = file_number +1
        write_to_File(file_text,file_number)  # Writing the final string to file
    if numline == 0:
        data_socket.send(b'Q')  # Send if received 0 as number of lines, terminate connection
    #data_socket.close()
    #listen_socket.close()

    # Replace this comment with your code.


# Add more methods here (Delete this line)
def read_header(data_socket):
    """
    This method reads the header only from the actual received message

    :return: the number of lines as a bytes object
    :rtype: int
    :author: Alaa Gaw
    """
    num = 0
    allread = b''
    while num < 4:
        # currRead = data_socket.recv(1)
        currRead = next_byte(data_socket)
        # currRead = data
        # print(currRead)
        num += 1
        allread = allread + currRead
  #      print(allread)
    return int.from_bytes(allread, 'big')


def read_message(numline, data_socket):
    """
   The method reads through the message in bytes

   :param int numline: How many lines the message contains, also used for a counter
   :return: the message, in a bytes object
   :rtype: bytes
   :author: Alex Sotelo
   """
    counter = 0
    msghave = b''
    while counter < numline:
        msgread = next_byte(data_socket)
        if msgread == b'\n':
            counter += 1
        msghave = msghave + msgread
    return msghave


def write_to_File(message,file_number):
    """
    This method writes the payload of the received message to a text file

    :param str message: String object that are read from the actual message
    :author: Alaa Gaw
    """
    file_name = str(file_number) + ".txt"
    print(file_name)
    output_file = open(file_name, 'w+')
    output_file.write(str(message))
    output_file.close()


def next_byte(data_socket):
    """
    Read the next byte from the socket data_socket.
    The data_socket argument should be an open tcp data connection
    socket (either a client socket or a server data socket).
    It should not be a tcp server's listening socket.

    Read the next byte from the server.
    If the byte is not yet available, this method blocks (waits)
      until the byte becomes available.
    If there are no more bytes, this method blocks indefinitely.

    :param data_socket: The socket to read from
    :return: the next byte, as a bytes object with a single byte in it
    """
    return data_socket.recv(1)


# Invoke the main method to run the program.
main()




