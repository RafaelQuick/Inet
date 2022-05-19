import socket
from _thread import *
import threading
from turtle import left, right
print_lock = threading.Lock()
print_lock2 = threading.Lock()


class Player:
    def __init__(self, x, y, hp, atk):
        self.x = x
        self.y = y
        self.hp = 10
        self.atk = 0

    def move(x, y, direction):
        oldX = self.x
        oldY = self.y
        newX = self.x
        newY = self.y

        if direction == up:
            newX += 1
            
        elif direction == down:
            pass
        elif direction == right:
            pass
        elif direction == left:
            pass
# metoden keyboard.read_key() väntar på input
# whoseTurn ska vara funktionen som anropas när en knapp trycks

# 7x7
mapArray = [
    ["#","#","#","#","#","#","#"],
    ["#"," "," "," "," "," ","#"],
    ["#"," "," "," "," "," ","#"],
    ["#"," "," "," "," "," ","#"],
    ["#"," "," "," "," "," ","#"],
    ["#"," "," "," "," "," ","#"],
    ["#","#","#","#","#","#","#"]]

def threaded(c):
    while True:
        data = c.recv(1024)
        if not data:
            print('Bye')
             
            # lock released on exit
            print_lock.release()
            break
        data = data.decode(encoding='UTF-8')
        print(data)
        
        y = str(mapArray)
        c.send(y.encode(encoding='UTF-8', errors='replace'))
    c.close()    

def main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = 12345
        s.bind(('', port))
    except socket.error:
        print("nej det blev fel :(")

    try:
        s.listen(5)
        print("Server started!")
    except:
        print("abonenten kan inte svara just nu, vem är abonenteten?")
    while True:
        c, addr = s.accept()
        print_lock.acquire()
        c2, addr2 = s.accept()
        print_lock2.acquire()
        print("Fick anslutning från", addr)
        print("Fick anslutning från", addr2)
        start_new_thread(threaded, (c,))
        start_new_thread(threaded, (c2,))
        #c.send("whats up bitch".encode(encoding='UTF-8', errors='replace')) #om error på karaktär ersätt med frågetecken

    s.close()
        
main()
