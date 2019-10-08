# server for a game called 'alien shooter'
from datetime import datetime
from _thread import *
from classes import *
from os import path
import colorama
import pickle
import socket
import time
import sys

colorama.init()

server = ''
port = 8000

server_ip = socket.gethostbyname(server)
print(server_ip)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server,port))
except socket.error as e:
    str(e)

def log(message):
    print("["+ colorama.Fore.GREEN + datetime.now().strftime("%H:%M:%S") + colorama.Style.RESET_ALL + "] " + message)

# variables
chat_messages = []
current_player = 0
players = 0
player_list = []
players_pos = []
current_level = 1

current_level = int(input("Level:"))

s.listen(50)
log('server started, waiting for a connection...')

def get_pos(pos):
    pos = pos.split(",")
    return round(float(pos[0]), 2), round(float(pos[1]), 2)


def game_loop():
    while True:
        time.sleep(1)


def client(conn, addr, id):
    nick = 'Unnamed' 
    conn.send(str.encode('1'))
    p = Player()

    while True:
        try:
            data = conn.recv(2048*9).decode()
            data = data.split(";")

            reply = [[],[]] # [request, players, chat]

            if not data:
                log("disconnected")
                break

            if data[0].startswith("REQUEST"): # request
                log("{0} from {1}".format(str(data[0]),str(addr)))
                
                if data[0].startswith("REQUEST_LOAD_CHARACTER"):
                    global players
                    nick = data[0].split("-")[1]
                    p.set_variables(nick, id)
                    reply[0].append(p.load_data())

                    player_list.append(nick)
                    players += 1
                    players_pos.append(data[1])
                elif data[0].startswith("REQUEST_LOAD_LEVEL"):
                    reply[0].append(current_level)
                elif data[0].startswith("REQUEST_LOGOUT"):
                    conn.close()
                    log("player '{0}' disconnected!".format(nick))
                    break

            players_pos[player_list.index(nick)] = data[1]
            reply[1].append(players) # player number
            reply[1].append(player_list)
            reply[1].append(players_pos)

            players_pos[player_list.index(nick)] = get_pos(data[1])
            
            conn.sendall(str.encode(str(reply)))
            
        except socket.error as e:
            print(e)
            break
    
    log("connection lost to {0}".format(addr))

    players -= 1
    del players_pos[player_list.index(nick)]
    player_list.remove(nick)
    conn.close()
    return

while True:
    conn, addr = s.accept()
    log("connection from: {0}".format(addr))

    start_new_thread(client, (conn, addr, current_player))
    current_player += 1