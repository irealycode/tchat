import socket
import select
import errno
import sys, getopt
from colorama import Fore, Back, Style
from threading import Thread
from time import sleep
import readline
import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

def encrypt(source, key, encode=True):
    key = SHA256.new(key).digest()  
    IV = Random.new().read(AES.block_size)
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size
    source += bytes([padding]) * padding
    data = IV + encryptor.encrypt(source)
    return base64.b64encode(data).decode("latin-1") if encode else data

def decrypt(source, key, decode=True):
    if decode:
        source = base64.b64decode(source.encode("latin-1"))
    key = SHA256.new(key).digest()  
    IV = source[:AES.block_size]
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])
    padding = data[-1]
    if data[-padding:] != bytes([padding]) * padding:
        raise ValueError("Invalid padding...")
    return data[:-padding]

HEADER_LENGTH = 10
passcnnect = False
host0 = ''
host1 = ''
password = ''
argv = sys.argv[1:]
try:
  opts, args = getopt.getopt(argv,"hH:P:S:",["hfile=","pfile=","sfile"])
except getopt.GetoptError:
  print ('command not found ??')
  print ('-h for help')
  sys.exit(2)
for opt, arg in opts:
  if opt == '-h':
     print ('client.py -H <HOST> -P <PORT> -S <PASSWORD>')
     sys.exit()
  elif opt in ("-H", "--hfile"):
     host0 = arg
  elif opt in ("-P", "--pfile"):
     host1 = arg
  elif opt in ("-S", "--sfile"):
     password = arg
     
HOST = host0
PORT = int(host1)

try:
    server_sockets = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sockets.connect((HOST, PORT))
    server_sockets.setblocking(False)
    my_username = input("username: ")
    username = my_username.encode('utf-8')
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
    server_sockets.send(username_header + username)
    print(Fore.LIGHTGREEN_EX + 'logged in as ' + my_username + ' seccessfully.')

    def check_for_msg():
        while 1:
            sleep(1)
            try:
                username_header = server_sockets.recv(HEADER_LENGTH)
                if not len(username_header):
                    print('Connection closed by the server')
                username_length = int(username_header.decode('utf-8').strip())
                username = server_sockets.recv(username_length).decode('utf-8')
                message_header = server_sockets.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = server_sockets.recv(message_length).decode('utf-8')
                message = decrypt(message,password.encode('utf-8')).decode('utf-8')
                print('\n'+Fore.WHITE + '[-' + Fore.GREEN + f'{username}' + Fore.WHITE + '-] : ' + Fore.YELLOW + f'{message}',end='')
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error: {}'.format(str(e)))
    
    t = Thread(target=check_for_msg)
    t.start()
    while 1:
        message = input(Fore.WHITE +'[-'+ Fore.CYAN + f'{my_username}' + Fore.WHITE + '-] : ')
        if message == 'exit -y':
            print(Fore.GREEN + "goodbye." + Fore.RESET)
        if len(message) <= 200:
            if message:
                message = encrypt(message.encode('utf-8'),password.encode('utf-8')).encode('utf-8')
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                server_sockets.send(message_header + message)
        elif len(message) > 200:
            print("you can't send messages that are longer than 200 characters")
            print("your message is " + str(len(message)) + " characters long")


    
except:
    print("error connecing")
