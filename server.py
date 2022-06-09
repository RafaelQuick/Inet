from base64 import encode
import socket
from _thread import *
import threading
import random
import time

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
        self.hp = hp
        self.atk = atk

    def move(self, direction):
        seed = random.randint(0, 40) # occasionally places a new powerup
        if seed == 0:
            placePowerups(1)
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
    global mapArray
    mapArray = []
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
        if mapArray[y][x] == " ":
            emptySpot = True
    return x, y

def placePowerups(number):    
    for i in range(number):
        x, y = genCoords()
        mapArray[y][x] = "?"
        
def createPlayer(no):
    x, y = genCoords()
    player = Player(no, x, y, 10, 1)
    mapArray[y][x] = "@"
    return player

def checkSquare(x, y):
    try:
        if mapArray[y][x] == "#":
            return "wall"
        elif mapArray[y][x] == " ":
            return "floor"
        elif mapArray[y][x] == "?":
            return "powerup"
        elif mapArray[y][x] == "@":
            return "player"
    except:
        print(x, y)
        print(mapArray)

def powerup(player):
    seed = random.randint(0, 100)
    if seed < 40: # attack boost, 40% chance
        atkBoost = random.randint(1,4)
        player.atk += atkBoost
        msg = f"Player {str(player.no)} feels {str(atkBoost)} muscles stronger!"
    elif seed >= 40 and seed < 60: # health boost, 20% chance
        if player.hp <= 7:
            player.hp += 3
        else: 
            player.hp = 10
        msg = f"Player {str(player.no)} chugs some good health juice!"
    elif seed >= 60 and seed < 70: # self harm, 10% chance
        player.hp -= 1
        msg = f"Player {str(player.no)} stubs their toe..."
    elif seed >= 70: # moves the player a random distance in a random direction, 30% chance
        displace(player, 2, 6)
        msg = f"Player {str(player.no)} has been displaced!"
    mapArray[no_y] = f"Player 1: {player1.hp} hp        Player 2: {player2.hp} hp"
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
    global mapArray
    global stopFlag
    if attacker_no == 1: # checks who is making the attack
        player2.hp -= player1.atk # decreases other players health
        mapArray[no_y] = f"Player 1: {player1.hp} hp        Player 2: {player2.hp} hp" # updates healthbars
        mapArray[no_y+1] = f"player1 attacks player2 for {player1.atk} damage!" # tells players what happened

        if player2.hp <= 0: # handles player death
            mapArray[no_y+1] = f"___player1 kills their opponent and wins the game!!____"
            time.sleep(2)
            mapArray = "exit" # sends exit message to clients
            stopFlag = True

    else:
        player1.hp -= player2.atk
        mapArray[no_y] = f"Player 1: {player1.hp} hp        Player 2: {player2.hp} hp"
        mapArray[no_y+1] = f"player2 attacks player1 for {player2.atk} damage!"
        
        if player1.hp <= 0:
            mapArray[no_y+1] = f"___player2 kills their opponent and wins the game!!____"
            time.sleep(2)
            mapArray = "exit"
            stopFlag = True


#____________MESSAGES____________

def encodeMessage(message):
    return message.encode(encoding='UTF-8', errors='replace')

def welcome(client, no):
    no = str(no)
    message = "Välkommen spelare " + no + "\n"
    client.send(message.encode(encoding='UTF-8', errors='replace'))

def introMessage(client):
    client.send(encodeMessage("------------ SPELREGLER ------------\n"))
    time.sleep(1)
    client.send(encodeMessage("1. Du (@) börjar med 10 enheter livslust.\n"))
    time.sleep(1)
    client.send(encodeMessage("2. Ditt mål är att hålla igång livslusten och ha ihjäl din motståndare (@)!\n"))
    time.sleep(1)
    client.send(encodeMessage("3. Det finns coola grejor (?) att plocka upp på marken.\n"))
    time.sleep(1)
    client.send(encodeMessage("4. Använt piltangenterna för att flytta på dig!\n"))
    time.sleep(1)
    client.send(encodeMessage("Tryck på en av piltangenterna för att börja\n"))
    client.send(encodeMessage("ready")) # startsignal att gå vidare till klientens logik
    time.sleep(0.2)


#____________SERVER LOGIC____________
def threaded(c, player):
    introMessage(c)
    global sendFlag
    global stopFlag
    while True:
        try:
            if stopFlag:
                c.send(encodeMessage(f"exit from player {str(player.no)}")) #ser till att skicka till båda
                stopFlag = True
                # lock released on exit
                c.close()
                return
                
                
            data = c.recv(16384) # servern väntar på att få något
            data = data.decode(encoding='UTF-8') # up, down, left, right
            if not stopFlag:
                player.move(data) # för att inte råka göra en player move mellan då trådarna håller på att stängas
            #print("sendflag truee")
            sendFlag = True # när flyttat, hissa upp flaggan och säg åt tredje tråden att skicka till båda spelarna
            # göra någonting med datan här
        except ConnectionResetError:
            stopFlag = True
            # lock released on exit
            c.close()
            return

        

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
        if stopFlag:
            break

def main():
    global sendFlag
    global stopFlag
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
        stopFlag = False
        sendFlag = False
        genMap()
        placePowerups(3)
        global player1
        global player2
        player1 = createPlayer(1)
        player2 = createPlayer(2)
        c, addr = s.accept()
        print("Fick anslutning från", addr, ", spelare 1 ")
        t1 = threading.Thread(target=threaded, args=[c, player1])
        welcome(c, 1)
        c.send(encodeMessage("Väntar på spelare 2"))
        c2, addr2 = s.accept()
        t2 = threading.Thread(target=threaded, args=[c2, player2])
        print("Fick anslutning från", addr2, ", spelare 2 ")
        welcome(c2, 2)
        c.send(encodeMessage("Spelare 2 är nu ansluten redo att starta"))
        #skapa spelarobjekten här innan trådarna
        t3 = threading.Thread(target=sendThread, args=[c, c2])
        t1.start()
        t2.start()
        t3.start()
        t1.join()
        t2.join()
        t3.join()
        #start_new_thread(threaded, (c, player1)) # klienterna har varsin tråd
        #start_new_thread(threaded, (c2, player2))
        #start_new_thread(sendThread, (c, c2)) # tråd 3 för skickandet
        print("Klienterna har avanslutits, väntar på nya klienter")
        #c.send("whats up bitch".encode(encoding='UTF-8', errors='replace')) # om error på karaktär ersätt med frågetecken
        
main()