import sys, os

# need to filter both incoming and outgoing packets

def bitmask(r_ip, p_ip):

    # if rule has '*', then any ip is accepted so return as accepted
    if r_ip == "*":
        return True

    # get and separate ip from rule
    ip = r_ip.split("/", 1)[0]
    r_bits = int(r_ip.split("/", 2)[1])

    r_ip1 = int(ip.split(".", 1)[0])
    r_ip2 = int(ip.split(".", 2)[1])
    r_ip3 = int(ip.split(".", 3)[2])
    r_ip4 = int(ip.split(".", 4)[3])

    # get and separate ip from packet
    ip = p_ip.split("/", 1)[0]

    p_ip1 = int(ip.split(".", 1)[0])
    p_ip2 = int(ip.split(".", 2)[1])
    p_ip3 = int(ip.split(".", 3)[2])
    p_ip4 = int(ip.split(".", 4)[3])

    # create the netmask
    mask = 0b00000000
    mask1 = 0
    mask2 = 0
    mask3 = 0
    mask4 = 0

    # get rules' ip and packet's ip into bit-format, and compare through that
    for i in range(1,r_bits+1):
        # restart ever 8 bits
        if (i == 9 or i == 17  or i == 25):
            mask = 0b00000000
        mask = mask >> 1
        mask = mask | 0b10000000
        # separate to four bytes
        if (i <= 8):
            mask1 = mask
        elif (i <= 16 and i > 8):
            mask2 = mask
        elif (i <= 24 and i > 16):
            mask3 = mask
        else:
            mask4 = mask
    #print(bin(mask1),".",bin(mask2),".",bin(mask3),".",bin(mask4))

    ip1 = mask1 & p_ip1
    ip2 = mask2 & p_ip2
    ip3 = mask3 & p_ip3
    ip4 = mask4 & p_ip4

    r_ip1 = mask1 & r_ip1
    r_ip2 = mask2 & r_ip2
    r_ip3 = mask3 & r_ip3
    r_ip4 = mask4 & r_ip4

    #print(mask1,".",mask2,".",mask3,".",mask4)
    #print("ip",ip1,".",ip2,".",ip3,".",ip4)
    #print("r_ip",r_ip1,".",r_ip2,".",r_ip3,".",r_ip4)
    if ip1==r_ip1 and ip2==r_ip2 and ip3==r_ip3 and ip4==r_ip4:
        return True
    else:
        return False

def get_ports(r_port, port):
    # if no comma, no ports to be separated
    if "," not in r_port or r_port == "*":
        return r_port

    ports = r_port.split(",")

    for p in ports:
        if p == port:
            return p

    return False

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
        if DEBUG: print("i",i+1)
        #print("rules:", rules[i][2])

        # check direction
        if rules[i][1] == direction:
            d_match = 1
        else: d_match = 0
        if DEBUG: print("direction:",rules[i][1], direction, "match:", d_match)

        # check IP
        if bitmask(rules[i][3], ip):
            ip_match = 1
        else: ip_match = 0
        if DEBUG: print("bitmask",bitmask(rules[i][3], ip), "match:", ip_match)

        # check port
        port_result = get_ports(rules[i][4], port)
        if port_result == "*":
            port_match = 1
        elif port_result == port:
            port_match = 1
        elif port_result == False:
            port_match = 0
        else: port_match = 0

        #if rules[i][4] == port or rules[i][4] == "*":
        #    port_match = 1
        #else: port_match = 0
        if DEBUG: print("port:", rules[i][4], port, "match:", port_match)

        # check if established connection
        # turn the flag into an int and check
        f = int(flag)
        if rules[i][5] == "":
            establish = 1
        elif rules[i][5] == "established" and f == 1:
            establish = 1
        else:
            establish = 0
        if DEBUG: print("establishment:", rules[i][5], f, "match:", establish)

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

        # ignore empty lines or comments
        if len(line) == 0 or line[0] == "#":
            continue

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
    #print("packet:",line, end="", file=sys.stdout)
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
