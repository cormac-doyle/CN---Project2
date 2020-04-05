import socket
import select
import errno
import sys

HEADER_LENGTH = 20

IP = "127.0.0.1"
PORT = 1234


username = input("Shop Name: ")
username = 'ShopServer - ' + username
counter = 0;

# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a given ip and port
client_socket.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
client_socket.setblocking(False)

# Prepare username and header and send them
# We need to encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well

username = username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)



#-----------------------------------------------------------------------------------

PORT_SHOP = 5678
# Creates socket
# socket.AF_INET - address family
# socket.SOCK_STREAM - TCP
server_shop_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# SO_ - socket option
# SOL_ - socket option level
# Sets REUSEADDR (as a socket option) to 1 on socket
server_shop_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Bind so server informs operating system that it's going to use given IP and port
# For a server using 0.0.0.0 means to listen on all available interfaces, useful to connect locally to 127.0.0.1 and remotely to LAN interface IP
server_shop_socket.bind((IP, PORT_SHOP))

# Listen to new connections
server_shop_socket.listen()
# Array of sockets for select.select()
shop_sockets_list = [server_shop_socket]

# List of clients - socket as a key, user header, name as data
shop_clients = {}

print(f'Listening for connections on {IP}:{PORT_SHOP}...')


#-----------------------------------------------------------------------------------
def receive_message(client_shop_socket):
    try:

        # Receive our "header" containing message length, it's size is defined and constant
        message_header_shop = client_shop_socket.recv(HEADER_LENGTH)

        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header_shop):
            return False

        # Convert header to int value
        message_length = int(message_header_shop.decode('utf-8').strip())

        # Return an object of message header and message data
        return {'header': message_header_shop, 'data': client_shop_socket.recv(message_length)}

    except:

        # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
        # or just lost his connection
        # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
        # and that's also a cause when we receive an empty message

        return False


#-----------------------------------------------------------------------------------


message_decoded = ''

while True:

    read_sockets, _, exception_sockets = select.select(shop_sockets_list, [], shop_sockets_list)

    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_shop_socket:

            # Accept new connection
            # That gives us new socket - client socket, connected to this given client only, it's unique for that client
            # The other returned object is ip/port set
            client_shop_socket, client_address = server_shop_socket.accept()

            # Client should send his name right away, receive it
            user = receive_message(client_shop_socket)

            # If False - client disconnected before he sent his name
            if user is False:
                continue

            # Add accepted socket to select.select() list
            shop_sockets_list.append(client_shop_socket)

            # Also save username and username header
            shop_clients[client_shop_socket] = user

            print('New Connection {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

            # Else existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)

            # If False, client disconnected, cleanup
            if message is False:
                print('Closed Connection: {}'.format(shop_clients[notified_socket]['data'].decode('utf-8')))

                # Remove from list for socket.socket()
                shop_sockets_list.remove(notified_socket)

                # Remove from our list of users
                del shop_clients[notified_socket]

                continue

            # Get user by notified socket, so we will know who sent the message
            user = shop_clients[notified_socket]

            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            message_decoded = str(message["data"].decode("utf-8"))

            if message_decoded == 'ENTRY':
                counter = counter + 1

            if message_decoded == 'EXIT':
                counter = counter - 1

            # If message not empty - send it
            if message_decoded:

                message_decoded = str(counter)  # store counter in message
                # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
                message_decoded = message_decoded.encode('utf-8')
                message_header = f"{len(message_decoded):<{HEADER_LENGTH}}".encode('utf-8')
                client_socket.send(message_header + message_decoded)



    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:
        # Remove from list for socket.socket()
        shop_sockets_list.remove(notified_socket)

        # Remove from our list of users
        del shop_clients[notified_socket]