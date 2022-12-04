#!/usr/bin/python3
from ast import For
import curses
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

my_username = ''
messages = []


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
host0 = '127.0.0.1'
host1 = '4242'
password = ''
argv = sys.argv[1:]
exitt = False
offline = True
try:
  opts, args = getopt.getopt(argv,"hH:P:S:",["hfile=","pfile=","sfile"])
except getopt.GetoptError:
  print ('command not found ??')
  print ('-h for help')
  sys.exit(2)
for opt, arg in opts:
  if opt == '-h':
     print ('client.py -H <HOST> -P <PORT> -S <KEY>')
     sys.exit()
  elif opt in ("-H", "--hfile"):
     host0 = arg
  elif opt in ("-P", "--pfile"):
     host1 = arg
  elif opt in ("-S", "--sfile"):
     password = arg
     
HOST = host0
PORT = int(host1)

banner="""▄▄▄▄▄ ▄▄·  ▄  .▄ ▄▄▄· ▄▄▄▄▄
•██  ▐█ ▌ ▪██▪ ▐█▐█ ▀█ •██  
 ▐█.▪██ ▄▄██▀ ▐█▄█▀▀█  ▐█.▪
 ▐█▌·▐███▌██▌▐▀▐█  ▪▐▌ ▐█▌·
 ▀▀▀ ·▀▀▀ ▀▀▀ · ▀    ▀  ▀▀▀ 
        tchat v1.0
    made by irealycode
https://github.com/irealycode
"""

def main(stdscr):
    global exitt
    msg = ''
    curses.echo()
    curses.use_default_colors()
    stdscr.bkgd(curses.COLOR_BLACK)
    for i in range(0, curses.COLORS):
        curses.init_pair(i, i, -1);
    stdscr.nodelay(True)
    
    while 1:
        if my_username == '' or ' ' in my_username:
            print(Fore.RED + f'cant leave username empty & no spaces'+Fore.RESET)
            exitt = True
            break
        # messages.append(['ok','ok'])
        # check_for_msg()
        stdscr.addstr(0,0,banner,curses.color_pair(69))
        if stdscr.getmaxyx()[0]-9 == len(messages):
            messages.pop(0)
        for i in range(len(messages)):
            stdscr.addstr(i+9,0,'[-',curses.color_pair(253))
            clr = ''
            clr1 = ''
            if messages[i][0] == my_username:
                clr = curses.color_pair(38)
                clr1 = curses.color_pair(253)
            else:
                clr = curses.color_pair(83)
                clr1 = curses.color_pair(178)
            stdscr.addstr(i+9,2,f'{messages[i][0]}',clr)
            stdscr.addstr(i+9,len(messages[i][0])+2,'-]:',curses.color_pair(253))
            stdscr.addstr(i+9,len(messages[i][0])+5,'',)
            stdscr.addstr(i+9,len(messages[i][0])+6,messages[i][1],clr1)
        stdscr.addstr(stdscr.getmaxyx()[0] - 1,0,'[-',curses.color_pair(253))
        stdscr.addstr(stdscr.getmaxyx()[0] - 1,2,f'{my_username}',curses.color_pair(38))
        stdscr.addstr(stdscr.getmaxyx()[0] - 1,len(my_username)+2,f'-]: {msg} ',curses.color_pair(253))
        try:
            s = stdscr.getkey(stdscr.getmaxyx()[0] - 1,len(my_username)+len(msg)+6)
            if s != '\n' and 'KEY' not in s:
                msg = msg + s
                stdscr.clear()
            elif s == 'KEY_BACKSPACE':
                msg = msg[:len(msg)-1]
                stdscr.clear()
            elif s == '\n':
                if msg != '' and msg != 'exit -y':
                    messages.append([my_username,msg])
                    send_message(msg)
                    msg = ''
                    stdscr.clear()
                elif msg == 'exit -y':
                    exitt = True
                    break
            else:
                pass
        except:
            pass
        # s = stdscr.getstr(stdscr.getmaxyx()[0] - 1,11, 200)
        stdscr.refresh()
    curses.endwin()

def send_message(message):
    if message == 'exit -y':
            print(Fore.GREEN + "goodbye." + Fore.RESET)
            exit()
    if len(message) <= 200:
        if message:
            message = encrypt(message.encode('utf-8'),password.encode('utf-8')).encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            server_sockets.send(message_header + message)

def check_for_msg():
    while 1:
        # exit()
        if exitt:
            exit()
        sleep(0.7)
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
            messages.append([username,message])
        except:
            pass

try:
    t = Thread(target=check_for_msg)
    t.start()
    try:

        server_sockets = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sockets.connect((HOST, PORT))
        server_sockets.setblocking(False)
        offline = False
        my_username = input("username: ")
        if password == '':
            password = input('key: ')
        if my_username == '' or ' ' in my_username:
            print(Fore.RED + f'cant leave username empty & no spaces'+Fore.RESET)
        else:
            username = my_username.encode('utf-8')
            username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
            server_sockets.send(username_header + username)
            print(Fore.LIGHTGREEN_EX + 'logged in as ' + my_username + ' seccessfully.')
    except:
        print(Fore.RED + f'server {HOST}:{PORT} is offline'+Fore.RESET)
except KeyboardInterrupt:
    print('goodbye.')
    exitt = True
    exit()



if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print('goodbye.')
        exitt = True
        exit()
