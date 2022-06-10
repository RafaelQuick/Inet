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
        self.no = no # håller reda på om man är spelare 1 eller 2
        self.x = x # x och y randomgenereras i början
        self.y = y
        self.hp = hp
        self.atk = atk

    def move(self, direction):
        seed = random.randint(0, 40) # placerar ut en ny powerup då och då när någon tar ett steg
        if seed == 0:
            placePowerups(1)
        oldX = self.x
        oldY = self.y
        newX = self.x
        newY = self.y

        # ändrar koordinaten beroende på vilken riktning man går i
        if direction == "up":
            newY -= 1
        elif direction == "down":
            newY += 1
        elif direction == "right":
            newX += 1
        elif direction == "left":
            newX -= 1
        
        # kollar först vart vi är på väg, hanterar destinationen olika
        newSquare = checkSquare(newX, newY)
        if newSquare == "wall":
            return
        elif newSquare == "floor":
            # skriver om nya koordinaterna till att vara en spelare
            # gamla koordinaterna blir nu tom mark
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
            # man kan inte gå in i varandra ;^)
            combat(self.no)
            return


def genMap():
    # koordinater skrivs mapArray[y][x]
    global mapArray
    mapArray = []
    innerMapArray = []
    for y in range(no_y):
        for x in range(no_x):
            # sätter ut väggar runt kanten, tom mark annars
            if x == 0 or y == 0 or x == (no_x-1) or y == (no_y-1):
                innerMapArray.append("#")
            else:
                innerMapArray.append(" ")
        mapArray.append(innerMapArray)
        innerMapArray = []
    # under spelplanen finns spelarnas hp. sista raden berätter det senaste som hänt i spelet
    mapArray.append(f"Player 1: {10} hp        Player 2: {10} hp")
    mapArray.append("")
    

def genCoords():
    # plockar fram en random tom ruta, används lite här och där
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
    # kollar vad som finns på ett givet koordinatpar
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
    seed = random.randint(0, 100) # för att kunna ha olika viktade chanser
    if seed < 40: # attack boost, 40% chans
        atkBoost = random.randint(1,4)
        player.atk += atkBoost
        msg = f"Player {str(player.no)} feels {str(atkBoost)} muscles stronger!"

    elif seed >= 40 and seed < 60: # helar hp, 20% chans
        if player.hp <= 7:
            player.hp += 3
        else: 
            player.hp = 10
        msg = f"Player {str(player.no)} chugs some good health juice!"

    elif seed >= 60 and seed < 70: # self harm, 10% chans
        player.hp -= 1
        msg = f"Player {str(player.no)} stubs their toe..."

    elif seed >= 70: # flyttar spelaren ett random avstånd i en random riktning , 30% chans
        displace(player, 2, 6)
        msg = f"Player {str(player.no)} has been displaced!"
    # uppdaterar hp-display och infodisplay    
    mapArray[no_y] = f"Player 1: {player1.hp} hp        Player 2: {player2.hp} hp"
    mapArray[no_y+1] = msg


def displace(player, min_dist, max_dist):
    # plockar en random riktning och flyttar spelaren inom ett avståndsrange
    directionSeed = random.randint(0, 3)
    distanceSeed = random.randint(min_dist, max_dist)
    if directionSeed == 0:
        direction = "up"
    elif directionSeed == 1:
        direction = "down"
    elif directionSeed == 2:
        direction = "right"
    elif directionSeed == 3:
        direction = "left"
    for i in range(distanceSeed):
        player.move(direction)


def combat(attacker_no):
    # hanterar global konflikt, som i Supremacy 1914
    global mapArray
    global stopFlag

    if attacker_no == 1: # kollar vem som initierat attacken
        player2.hp -= player1.atk # minskar andra spelarens hp
        mapArray[no_y] = f"Player 1: {player1.hp} hp        Player 2: {player2.hp} hp" # uppdaterar hp-display
        mapArray[no_y+1] = f"player1 attacks player2 for {player1.atk} damage!" # uppdaterar infodisplay

        if player2.hp <= 0: # hanterar döden (5 steg)
            mapArray[no_y+1] = f"----player1 kills their opponent and wins the game!!----"
            time.sleep(2)
            mapArray = "exit" # skickar exit-meddelande till klienterna
            stopFlag = True
    # samma skit för spelare 2
    else:
        player1.hp -= player2.atk
        mapArray[no_y] = f"Player 1: {player1.hp} hp        Player 2: {player2.hp} hp"
        mapArray[no_y+1] = f"player2 attacks player1 for {player2.atk} damage!"
        
        if player1.hp <= 0:
            mapArray[no_y+1] = f"----player2 kills their opponent and wins the game!!----"
            time.sleep(2)
            mapArray = "exit"
            stopFlag = True


#____________MESSAGES____________

def encodeMessage(message):
    return message.encode(encoding='UTF-8', errors='replace')


def welcome(client, no):
    no = str(no)
    message = "Welcome player " + no + "\n"
    client.send(message.encode(encoding='UTF-8', errors='replace'))


def introMessage(client):
    client.send(encodeMessage("------------ Game Rules ------------\n"))
    time.sleep(1)
    client.send(encodeMessage("1. You (@) start with 10 hitpoints.\n"))
    time.sleep(1)
    client.send(encodeMessage("2. Your goal is to stay alive and kill your opponent (@) !\n"))
    time.sleep(1)
    client.send(encodeMessage("3. There are cool powerups (?) on the ground, just walk into them.\n"))
    time.sleep(1)
    client.send(encodeMessage("4. Use the arrow keys to move!\n"))
    time.sleep(1)
    client.send(encodeMessage("Press any arrow key to begin.\n"))
    client.send(encodeMessage("ready")) # startsignal att gå vidare till klientens logik
    time.sleep(0.2)


#____________SERVER LOGIC____________
def threaded(c, player):
    # tråd som tar emot data från EN (1) klient, och säger när vi kan skicka data till klienterna
    introMessage(c)
    global sendFlag
    global stopFlag
    while True:
        try:
            if stopFlag:
                c.send(encodeMessage(f"exit from player {str(player.no)}")) # skickar stoppsignal till klienterna
                stopFlag = True
                # lock released on exit
                c.close()
                return
                
            data = c.recv(16384) # servern väntar på att få något
            data = data.decode(encoding='UTF-8') # up, down, left, right
            if not stopFlag:
                player.move(data) # vill inte move när vi ska avsluta
            sendFlag = True # hissa upp sendFlag vilket säger åt tredje tråden att göra sin grej (se nedan)

        except ConnectionResetError:
            stopFlag = True
            c.close()
            return
        

def sendThread(c1, c2):
    # tråd som skickar spelplanen till klienterna när sendFlag hissas
    while True:
        global sendFlag
        if sendFlag:
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
        print("Socket error")

    try:
        s.listen(5)
        print("Server started!")
    except:
        print("Server failed connection")
    while True:
        stopFlag = False
        sendFlag = False
        genMap()
        placePowerups(3)
        # skapa spelarobjekten som ska skickas med trådarna
        global player1
        global player2
        player1 = createPlayer(1)
        player2 = createPlayer(2)
        c, addr = s.accept()

        print("Player one has connected from ", addr)
        # skapa tråd 1 och 2 för att ta emot input från varsin klient
        t1 = threading.Thread(target=threaded, args=[c, player1])
        welcome(c, 1)
        c.send(encodeMessage("Waiting for player 2"))
        c2, addr2 = s.accept()
        t2 = threading.Thread(target=threaded, args=[c2, player2])
        print("Player two has connected from ", addr)
        welcome(c2, 2)
        c.send(encodeMessage("Player 2 is now connected and ready to play!"))
        # tråd 3 hanterar skickande av data till klienterna
        t3 = threading.Thread(target=sendThread, args=[c, c2])

        t1.start()
        t2.start()
        t3.start()
        # joinar trådarna så att de avslutas samtidigt
        t1.join()
        t2.join()
        t3.join()
        # vi kommer bara hit när trådarna avslutas
        print("Both clients have disconnected, waiting for new connections...")       
main()