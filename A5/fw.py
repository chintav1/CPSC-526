import sys, os

# need to filter both incoming and outgoing packets

def bitmask(ip):
    ip = ip.split("/", 1)[0]
    bits = int(ip.split("/", 2)[1])

    ip1 = int(ip.split(".", 1)[0])
    ip2 = int(ip.split(".", 2)[1])
    ip3 = int(ip.split(".", 3)[2])
    ip4 = int(ip.split(".", 4)[3])

    return

def firewall(rules, direction, ip, port, flag):
    # go through all rules and see if it matches the other four things
    # if it does, do what the rules says
    # if not, reject
    d_match = 0
    ip_match = 0
    port_match = 0
    establish = 0
    DEBUG = False
    #print(len(rules))
    for i in range(0, len(rules)):
        #print("i",i+1)
        #print("rules:", rules[i][2])
        if DEBUG: print("direction:",rules[i][1], direction)
        if rules[i][1] == direction:
            d_match = 1
        else: d_match = 0

        if DEBUG: print("ip:",rules[i][3], ip)
        if rules[i][3] == ip or rules[i][3] == "*":
            ip_match = 1
        else: ip_match = 0

        if DEBUG: print("port:", rules[i][4], port)
        if rules[i][4] == port or rules[i][4] == "*":
            port_match = 1
        else: port_match = 0

        # turn the flag into an int and check
        f = int(flag)
        if rules[i][5] == "":
            establish = 1
        elif rules[i][5] == "established" and f == 1:
            establish = 1
        else:
            establish = 0

        # figure out what to do with packet
        # if all match, do exactly as rule says
        # return which rule number to follow
        #print("Rules",rules[i])
        if d_match == 1 and ip_match == 1 and port_match == 1 and establish == 1:
            #print("Rules:",rules[i])
            return str(i+1) + " " + rules[i][2]
    # if reaches here, then no rules for this packet, so reject

    return "drop"







# start, first read rules from configuration file
# configuration file specified on command line

# list of rules will be saved
# list of lists
# line number for rule, direction, action, ip, port, flag

#################
##### Rules #####
#################
rules = [[]]

linenum = 0
flag = ""
config_file = sys.argv[1]
with open(config_file, "r") as f:
    line = sys.stdin.buffer.readline()
    for line in f:
        # split string to be put into a list
        line = line.replace("\n", "")
        line.strip("\t")
        line = " ".join(line.split())

        direction = line.split(" ", 1)[0]
        action = line.split(" ", 2)[1]
        ip = line.split(" ", 3)[2]
        port = line.split(" ", 4)[3]
        if len(line.split(" ")) == 5:
            flag = line.split(" ", 5)[4]
        else:
            flag = ""
        if linenum == 0:
            rules[linenum] = [linenum+1, direction, action, str(ip), str(port), flag]
        else:
            rules.append([linenum+1, direction, action, str(ip), str(port), flag])
        print(rules[linenum])
        linenum = linenum + 1
f.close()


# packets read in from standard input
# program reads from standard input until EOF, then should terminate

###################
##### Packets #####
###################

# direction, ip, port, flag
packet = ["", "", "", ""]
for line in sys.stdin:
    print("packet:",line, end="", file=sys.stdout)
    line = line.replace("\n", "")
    line.strip("\t")

    direction = line.split(" ", 1)[0]
    ip = line.split(" ", 2)[1]
    port = line.split(" ", 3)[2]
    flag = line.split(" ", 4)[3]


    # time to accept, reject, or drop
    decision = firewall(rules, direction, ip, port, flag)
    if decision == "drop":
        # do the drop output
        print("drop() "+direction+" "+ip+" "+port+" "+flag, file=sys.stdout)
    else:
        # if doesn't say drop, then do action
        linenum = decision.split(" ", 1)[0]
        action = decision.split(" ", 2)[1]
        print(action+"("+linenum+") "+direction+" "+ip+" "+port+" "+flag, file=sys.stdout)

















#
