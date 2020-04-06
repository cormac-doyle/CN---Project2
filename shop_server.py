import csv
import socket
import select
import errno
import sys
from _csv import writer

HEADER_LENGTH = 20

IP = "127.0.0.1"
PORT = 1234
#my_username = input("Shop Name: ")

my_id = input("Shop Name: ")

my_id = my_id
my_username = my_id

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

username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)

def checkStock(itemid):
    itemid = str(itemid)
    with open('Stocklist.csv', mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')  # open the database
        rows = list(csv_reader)  # store rows of database in rows
        length = len(rows)  # find the number of rows
        i = 0
        while i != length:
            if rows[i][0] == itemid:
                break  # break when the item id  has been located in the database
            else:
                i = i + 1
            # when the while loop finishes i will store the line number the item id was found on
        if i == length:
            print("Invalid item ID")
            csv_file.close()
            return 0
        else:
            itemquantity = int(rows[i][2]) #set the itemquantity to the quantity of the item searched
            csv_file.close()
            return itemquantity

def tillPurchase(itemid):
    itemid = str(itemid)
    with open('Stocklist.csv', mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')  # open the database
        rows = list(csv_reader)  # store rows of database in rows
        length = len(rows)  # find the number of rows

        i = 0
        while i != length:
            if rows[i][0] == itemid:
                break  # break when the item id  has been located in the database
            else:
                i = i + 1
            # when the while loop finishes i will store the line number the item id was found on
        if i == length:
            print("Invalid item ID")
            csv_file.close()
            return 0
        else:
            itemquantity = int(rows[i][2]) #set the itemquantity to the quantity of the item searched
            itemquantity = itemquantity - 1 # decrement the quantity
            rows[i][2] = str(itemquantity)
            csv_file.close()
            my_new_csv = open('Stocklist.csv', 'w', newline='')
            csv_writer = csv.writer(my_new_csv)
            csv_writer.writerows(rows)  # write back to the file the updated rows with the quantity modified
            my_new_csv.close()

def addStock(itemid,new_stock_quantity,itemname = 'item description not specified'):
    itemid = str(itemid)
    with open('Stocklist.csv', mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')  # open the database
        rows = list(csv_reader)  # store rows of database in rows
        length = len(rows)  # find the number of rows

        i = 0
        while i != length:
            if rows[i][0] == itemid:
                break  # break when the item id  has been located in the database
            else:
                i = i + 1
            # when the while loop finishes i will store the line number the item id was found on
        if i == length:
            csv_file.close()
            newline = [itemid,itemname,str(new_stock_quantity)]
            with open('Stocklist.csv','a+', newline='\n') as write_obj:
                # Create a writer object from csv module
                csv_writer = writer(write_obj)
                # Add contents of list as last row in the csv file
                csv_writer.writerow(newline)
        else:
            itemquantity = int(rows[i][2]) #set the itemquantity to the quantity of the item searched
            itemquantity = itemquantity + new_stock_quantity # add the new stock to the quantity
            rows[i][2] = str(itemquantity)
            csv_file.close()
            my_new_csv = open('Stocklist.csv', 'w', newline='\n')
            csv_writer = csv.writer(my_new_csv)
            csv_writer.writerows(rows)  # write back to the file the updated rows with the quantity modified
            my_new_csv.close()

while True:

    # Wait for user to input a message
    message = input(f'{my_username} > ')



    if message == 'ENTRY':
        counter = counter + 1


    if message == 'EXIT':
        counter = counter - 1



    # If message not empty - send it
    if message:

        message = str(counter)
        # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)

    try:

        while True:

            # Receive our "header" containing username length, it's size is defined and constant
            username_header = client_socket.recv(HEADER_LENGTH)

            # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()


    except IOError as e:
        # This is normal on non blocking connections - when there are no incoming data error is going to be raised
        # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
        # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
        # If we got different error code - something happened
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        # We just did not receive anything
        continue

    except Exception as e:
        # Any other exception - something happened, exit
        print('Reading error: '.format(str(e)))
        sys.exit()
