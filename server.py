import socket
from _thread import *
import threading
from turtle import left, right
print_lock = threading.Lock()
print_lock2 = threading.Lock()

# game shit
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
            newY += 1
        elif direction == down:
            newY -= 1
        elif direction == right:
            newX += 1
        elif direction == left:
            newX -= 1
        
        newSquare = checkSquare(newX, newY)
        if newSquare == "wall":
            pass
        elif newSquare == " ":
            mapArray[newY][newX] = "@"
            mapArray[oldY][oldX] = " "
        elif newSquare == "/":
            mapArray[newY][newX] = "@"
            mapArray[oldY][oldX] = " "
            self.atk += 5
        elif newSquare == "@":
            pass # implementera funktion för att hantera attacker mellan spelare
        mapArray[oldY][oldX] = " "
        self.x = newX
        self.y = newY
# 7x7 varav 5x5 spelbart, koordinater skrivs mapArray[y][x]

#######
#     #
#     #
#     #
#     #
#     #
#######

mapArray = [
    ["#","#","#","#","#","#","#"],
    ["#"," "," "," "," "," ","#"],
    ["#"," "," "," "," "," ","#"],
    ["#"," "," "," "," "," ","#"],
    ["#"," "," "," "," "," ","#"],
    ["#"," "," "," "," "," ","#"],
    ["#","#","#","#","#","#","#"]]

def checkSquare(x, y):
    global mapArray
    if mapArray[y][x] == "#":
        return "wall"
    elif mapArray[y][x] == " ":
        return "floor"
    elif mapArray[y][x] == "/":
        return "weapon"
    elif mapArray[y][x] == "@":
        return "player"


# server poop
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
        print("Abonenten du försöker nå, kan inte TA ditt samtal just nu.")
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
