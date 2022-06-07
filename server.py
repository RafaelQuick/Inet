from base64 import encode
import socket
from _thread import *
import threading
import random
from turtle import left, right
import time
print_lock = threading.Lock()
print_lock2 = threading.Lock()
print_lock3 = threading.Lock()
mapArray = []
no_x = 20
no_y = 20
sendFlag = False
stopFlag = False

#____________GAME LOGIC____________
class Player:
    def __init__(self, no, x, y, hp, atk):
        self.no = no
        self.x = x
        self.y = y
        self.hp = 10
        self.atk = 1

    def move(self, direction):
        oldX = self.x
        oldY = self.y
        newX = self.x
        newY = self.y

        if direction == "up":
            newY -= 1
        elif direction == "down":
            newY += 1
        elif direction == "right":
            newX += 1
        elif direction == "left":
            newX -= 1
        
        newSquare = checkSquare(newX, newY)
        if newSquare == "wall":
            return
        elif newSquare == "floor":
            mapArray[newY][newX] = "@"
            mapArray[oldY][oldX] = " "
            self.x = newX
            self.y = newY
        elif newSquare == "powerup":
            mapArray[newY][newX] = "@"
            mapArray[oldY][oldX] = " "
            self.x = newX
            self.y = newY
            powerup(self)
        elif newSquare == "player":
            combat(self.no)
            return


#koordinater skrivs mapArray[y][x]

def genMap():
    innerMapArray = []
    for y in range(no_y):
        for x in range(no_x):
            if x == 0 or y == 0 or x == (no_x-1) or y == (no_y-1):
                innerMapArray.append("#")
            else:
                innerMapArray.append(" ")
        mapArray.append(innerMapArray)
        innerMapArray = []
    mapArray.append(f"Player 1: {10} hp        Player 2: {10} hp")
    mapArray.append("")
    

def genCoords():
    emptySpot = False
    while emptySpot == False:
        x = random.randrange(1,(no_x-2))
        y = random.randrange(1,(no_y-2))
        print(str(x) + " " + str(y))
        if mapArray[y][x] == " ":
            emptySpot = True
    return x, y

def placePowerups():    
    for i in range(3):
        x, y = genCoords()
        mapArray[y][x] = "?"
        
def createPlayer(no):
    x, y = genCoords()
    player = Player(no, x, y, 10, 1)
    mapArray[y][x] = "@"
    return player

def checkSquare(x, y):
    if mapArray[y][x] == "#":
        return "wall"
    elif mapArray[y][x] == " ":
        return "floor"
    elif mapArray[y][x] == "?":
        return "powerup"
    elif mapArray[y][x] == "@":
        return "player"

def powerup(player):
    seed = random.randint(0, 3)
    if seed == 0:
        atkBoost = random.randint(1,4)
        player.atk += atkBoost
        msg = f"Player {str(player.no)} feels {str(atkBoost)} muscles stronger!"
    elif seed == 1:
        if player.hp <= 7:
            player.hp += 3
        else: 
            player.hp = 10
        msg = f"Player {str(player.no)} chugs some good health juice!"
    elif seed == 2:
        player.hp -= 1
        msg = f"Player {str(player.no)} stubs their toe..."
    elif seed == 3:
        # moves the player a random distance in a random direction
        displace(player, 2, 6)
        msg = f"Player {str(player.no)} has been displaced!"
    mapArray[no_y+1] = msg

def displace(player, min_dist, max_dist):
    directionSeed = random.randint(0, 3)
    distanceSeed = random.randint(min_dist, max_dist)
    if directionSeed == 0:
        direction = "up"
    elif directionSeed == 1:
        direction = "down"
    elif directionSeed == 2:
        direction = "left"
    elif directionSeed == 3:
        direction = "right"
    for i in range(distanceSeed):
        player.move(direction)

def combat(attacker_no):
    if attacker_no == 1:
        player2.hp -= player1.atk
        mapArray[no_y+1] = f"player1 attacks player2 for {player1.atk} damage!"
        mapArray[no_y] = f"Player 1: {player1.hp} hp        Player 2: {player2.hp} hp"
        if player2.hp == 0:
            mapArray[no_y+1] = f"___player1 kills their opponent and wins the game!!____"
    else:
        player1.hp -= player2.atk
        mapArray[no_y+1] = f"player2 attacks player1 for {player2.atk} damage!"
        mapArray[no_y] = f"Player 1: {player1.hp} hp        Player 2: {player2.hp} hp"
        if player1.hp == 0:
            mapArray[no_y+1] = f"___player2 kills their opponent and wins the game!!____"


#____________MESSAGES____________

def encodeMessage(message):
    return message.encode(encoding='UTF-8', errors='replace')

def welcome(client, no):
    no = str(no)
    message = "Välkommen spelare " + no + "\n"
    client.send(message.encode(encoding='UTF-8', errors='replace'))

def introMessage(client):
    client.send(encodeMessage("------------ SPELREGLER ------------\n"))
    client.send(encodeMessage("1. Du (@) börjar med 10 enheter livslust.\n"))
    client.send(encodeMessage("2. Ditt mål är att hålla igång livslusten och ha ihjäl din motståndare (@)!\n"))
    client.send(encodeMessage("3. Det finns coola grejor (?) att plocka upp på marken.\n"))
    time.sleep(1)
    client.send(encodeMessage("Spelet startar om: \n"))
    client.send(encodeMessage("3\n"))
    time.sleep(1)
    client.send(encodeMessage("2\n"))
    time.sleep(1)
    client.send(encodeMessage("1\n"))
    time.sleep(1)
    client.send(encodeMessage("ready")) #startsignal att gå vidare till klientens logik
    time.sleep(0.2)

def flagSet():
    sendFlag = True

#____________SERVER LOGIC____________
def threaded(c, player):
    introMessage(c)
    global sendFlag
    global stopFlag
    while True:
        data = c.recv(16384) #servern väntar på att få något
        if (not data) or stopFlag or (data == "quit"):
            print('Bye')
            stopFlag = True
            # lock released on exit
            print_lock.release()
            print_lock2.release()
            print_lock3.release()
            break
        data = data.decode(encoding='UTF-8') #up, down, left, right
        player.move(data)
        #print("sendflag truee")
        sendFlag = True #när flyttat, hissa upp flaggan och säg åt tredje tråden att skicka till båda spelarna
        #göra någonting med datan här
        
    c.close()    

def sendThread(c1, c2):
    #print("har lyckats starta skicka tråden")
    while True:
        global sendFlag
        if sendFlag:
            #print("nu ska jag skicka")
            y = str(mapArray)
            c1.send(y.encode(encoding='UTF-8', errors='replace'))
            c2.send(y.encode(encoding='UTF-8', errors='replace'))
            sendFlag = False
        

def main():
    genMap()
    placePowerups()
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
        print("1")
        print("Fick anslutning från", addr)
        print_lock.acquire()
        welcome(c, 1)
        c.send(encodeMessage("Väntar på spelare 2"))
        print("2")
        c2, addr2 = s.accept()
        print_lock2.acquire()
        print("Fick anslutning från", addr2)
        welcome(c2, 2)
        c.send(encodeMessage("Spelare 2 är nu ansluten redo att starta"))
        #skapa spelarobjekten här innan trådarna
        global player1
        global player2
        player1 = createPlayer(1)
        player2 = createPlayer(2)
        print_lock3.acquire()
        start_new_thread(threaded, (c, player1))
        start_new_thread(threaded, (c2, player2))
        start_new_thread(sendThread, (c, c2)) #tråd 3 för skickandet
        #c.send("whats up bitch".encode(encoding='UTF-8', errors='replace')) #om error på karaktär ersätt med frågetecken

    s.close()
        
main()
