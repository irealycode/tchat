import socket
import select
import errno
import sys, getopt
from colorama import Fore, Back, Style
from threading import Thread

HEADER_LENGTH = 10
passcnnect = False
host0 = ''
host1 = ''
argv = sys.argv[1:]
try:
  opts, args = getopt.getopt(argv,"hH:P:",["hfile=","pfile="])
except getopt.GetoptError:
  print (Fore.RED + 'command not found ??')
  print ('-h for help')
  sys.exit(2)
for opt, arg in opts:
  if opt == '-h':
     print ('client.py -H <HOST> -P <PORT>')
     sys.exit()
  elif opt in ("-H", "--hfile"):
     host0 = arg
  elif opt in ("-P", "--pfile"):
     host1 = arg
     
IP = host0
PORT = int(host1)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)
my_username = input("username: ")
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)

def receive():
    while True:
        try:
            msg = client_socket.recv(1024).decode("utf8")
            passw = input("room password: ")
            if passw == msg:
                print(Fore.LIGHTGREEN_EX + 'loged in as ' + my_username + ' seccessfully.')
                chatS()
            elif passw != msg:
                print("incorrect password!")
                break
        except OSError: 
            print("ok1")
            break


def chatS():
    while True:
        message = input(Fore.WHITE +'[-'+ Fore.CYAN + f'{my_username}' + Fore.WHITE + '-] : ')
        if message == 'exit -y':
            print("goodbye.")
            sys.exit()
        if message:
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(message_header + message)

        try:
            while True:
                username_header = client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    print('Connection closed by the server')
                    sys.exit()
                username_length = int(username_header.decode('utf-8').strip())
                username = client_socket.recv(username_length).decode('utf-8')
                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')
                print(Fore.WHITE + '[-' + Fore.GREEN + f'{username}' + Fore.WHITE + '-] : ' + Fore.YELLOW + f'{message}')

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()
            continue

        except Exception as e:
            print('error')
            sys.exit()




receive_thread = Thread(target=receive)
receive_thread.start()
