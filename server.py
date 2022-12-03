import socket
import select
import sys, getopt
from threading import Thread

HEADER_LENGTH = 10
from colorama import Fore, Back, Style
#cammand specify


correctpass = False
endwhile = False
host0 = ''
host1 = ''
password = ''
argv = sys.argv[1:]
clients = {}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sockets_list = [server_socket]
try:
  opts, args = getopt.getopt(argv,"hH:P:S:",["hfile=","pfile=","sfile"])
except getopt.GetoptError:
  print ('command not found ??')
  print ('-h for help')
  sys.exit(2)
for opt, arg in opts:
  if opt == '-h':
     print ('server.py -H <HOST> -P <PORT>')
     sys.exit()
  elif opt in ("-H", "--hfile"):
     host0 = arg
  elif opt in ("-P", "--pfile"):
     host1 = arg



HOST = host0
PORT = int(host1)

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())

        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False

def serverlisten():
    try:
        while True:
            read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
            if endwhile == True:
                print(Fore.GREEN + "goodbye." + Fore.RESET)
                break
            for notified_socket in read_sockets:
                if notified_socket == server_socket:
                    client_socket, client_address = server_socket.accept()
                    user = receive_message(client_socket)
                    if user is False:
                        continue
                    sockets_list.append(client_socket)
                    clients[client_socket] = user

                    print(Fore.LIGHTGREEN_EX +'new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')) + Fore.RESET)

                else:
                    message = receive_message(notified_socket)
                    if message is False:
                        print('Closed connection by: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                        sockets_list.remove(notified_socket)
                        del clients[notified_socket]

                        continue
                    user = clients[notified_socket]

                    print(Fore.LIGHTGREEN_EX +'Message from ' + Fore.BLUE + f'{user["data"].decode("utf-8")} : ' + Fore.YELLOW +  f'{message["data"].decode("utf-8")}' + Fore.RESET)
                    for client_socket in clients:
                        if client_socket != notified_socket:

                            client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

            for notified_socket in exception_sockets:
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
    except:
        print("error connecting")
        server_socket.close()




try:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print('listening on ' + HOST + ':' + str(PORT) + '...')
    serverlisten()
except:
    print("error conecting1")
