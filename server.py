import socket
import select
import sys, getopt

HEADER_LENGTH = 10
#cammand specify


correctpass = False
host0 = ''
host1 = ''
password = ''
argv = sys.argv[1:]
try:
  opts, args = getopt.getopt(argv,"hH:P:s:",["hfile=","pfile=","sfile"])
except getopt.GetoptError:
  print ('command not found ??')
  sys.exit(2)
for opt, arg in opts:
  if opt == '-h':
     print ('server.py -H <HOST> -P <PORT>')
     sys.exit()
  elif opt in ("-H", "--hfile"):
     host0 = arg
  elif opt in ("-P", "--pfile"):
     host1 = arg
  elif opt in ("-s", "--sfile"):
     password = arg



IP = host0
PORT = int(host1)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()
sockets_list = [server_socket]
clients = {}

print('Listening on ', host0 ,':', host1, '...')

def receive_message(client_socket):
        try:
            message_header = client_socket.recv(HEADER_LENGTH)
            if not len(message_header):
                return False
            message_length = int(message_header.decode('utf-8').strip())

            return {'header': message_header, 'data': client_socket.recv(message_length)}

        except:
            return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)
            if user is False:
                continue
            sockets_list.append(client_socket)
            clients[client_socket] = user

            print('new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

        else:
            message = receive_message(notified_socket)
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]

                continue
            user = clients[notified_socket]

            print(f'Message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
            for client_socket in clients:
                if client_socket != notified_socket:

                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
