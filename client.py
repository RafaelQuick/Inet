import socket
import keyboard
import time
from sys import exit
from os import system, name #name blir nu reserverad ord OBS.

def genHotkeys(s):
    keyboard.add_hotkey('uppil', lambda: onKeyPress('up', s))
    keyboard.add_hotkey('nedpil', lambda: onKeyPress('down', s))
    keyboard.add_hotkey('vänsterpil', lambda: onKeyPress('left', s))
    keyboard.add_hotkey('högerpil', lambda: onKeyPress('right', s))
    #keyboard.add_hotkey('quit', lambda: onKeyPress('ESC', s))
    
def onKeyPress(direction, s):
    #print(direction + " pressed")
    s.send(direction.encode(encoding='UTF-8'))

def introPhase(s):
    #s = server
    while True:
        data = s.recv(16384)
        data = data.decode(encoding='UTF-8')
        print(data)
        if data == "ready":
            break


def main():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    port = 12345
    print("Väntar på anslutning")
    connected = False
    for i in range(21):
        # printar om var 5:e sekund
        if i == 5 or i == 10 or i == 15: 
            print("Väntar på anslutning")
        elif i == 20:
            print("Kunde inte hitta koppling till servern")
            exit() #från sys modulen # more like sus modulen amirite
        try:
            s.connect(('172.17.1.22', port)) # Raffe: 192.168.0.102 | Nima: 192.168.1.126 | Fredrika: 172.17.1.22
            connected = True
            break
        except:
            time.sleep(1) # provar ansluta under en 20 sekunders period annars timeout
    if not connected:
        exit("Kunde inte hitta koppling till servern") #från sys modulen # more like sus modulen amirite
    print("Connected till host host")
    introPhase(s)
    genHotkeys(s)
    while True:
        data = s.recv(16384)
        data = data.decode(encoding='UTF-8')
        lista = eval(data)
        #if name == 'nt':
        #    system('CLS')
        #else:
        #    system('clear')
        for row in lista:
            newRow = ""
            for char in row:
                newRow += char
            print(newRow)
        if data == "exit":
            s.close()
    
main()

    
