import socket
import keyboard


def genHotkeys(s):
    print("hotkkeys genereate")
    keyboard.add_hotkey('uppil', lambda: onKeyPress('up', s))
    keyboard.add_hotkey('nedpil', lambda: onKeyPress('down', s))
    keyboard.add_hotkey('vänsterpil', lambda: onKeyPress('left', s))
    keyboard.add_hotkey('högerpil', lambda: onKeyPress('right', s))
    
def onKeyPress(direction, s):
    print(direction + " pressed")
    s.send(direction.encode(encoding='UTF-8'))
    data = s.recv(1024)
    data = data.decode(encoding='UTF-8')
    list = eval(data)
    for row in list:
        newRow = ""
        for char in row:
            newRow += char
        print(newRow)
    
    if data == "exit":
        s.close()


def main():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    port = 12345
    s.connect(('localhost', port))
    print("connected till host host")
    genHotkeys(s)
    while keyboard.read_key():
        pass
    
main()

    
