import sys, os

# need to filter both incoming and outgoing packets

def firewall(rules, direction, ip, port, flag):
    # go through all rules and see if it matches the other four things
    # if it does, do what the rules says
    # if not, reject
    d_match = 0
    ip_match = 0
    port_match = 0
    est_only = False
    for i in range(0, len(rules)):
        if rules[i][1] == direction:
            d_match = 1
        else: d_match = 0
        if rules[i][3] == ip or rules[i][3] == "*":
            ip_match = 1
        else: ip_match = 1
        if rules[i][4] == port or rules[i][4] == "*":
            port_match = 1
        else: port_match = 0
        if rules[i][5] == 1:
            est_only = True
        else: est_only = False

        # figure out what to do with packet
        # if all match, do exactly as rule says
        # return which rule number to follow
        if d_match == 1 and ip_match == 1 and port_match == 1 and (not est_only or (est_only and flag == 1)):
            return i

    # if reaches here, then no rules for this packet, so reject
    return "drop"







# start, first read rules from configuration file
# configuration file specified on command line

# list of rules will be saved
# list of lists
# line number for rule, direction, action, ip, port, flag


rules = [][0, "", "", "", "", ""]

linenum = 0
flag = ""
with open(config_file, "r") as f:
    line = sys.stdin.buffer.readline()
    for line in f:
        linenum = linenum + 1
        # this should get rid of tabs???
        line = " ".join([s.replace("\t", " ") for s in line])
        # hopefully these are all split properly
        direction = line.split(" ", 0)[1]
        action = line.split(" ", 1)[2]
        ip = line.split(" ", 2)[3]
        port = line.split(" ", 3)[4]
        if len(line.split(" ")) == 5:
            flag = line.split(" ", 4)[5]
        else:
            flag = ""
        rules[linenum-1] = [linenum, direction, action, str(ip), str(port), flag]
f.close()


# packets read in from standard input
# program reads from standard input until EOF, then should terminate

# direction, ip, port, flag
packet = ["", "", "", ""]
with open(packet_file, "r") as f:
    for line in f:
        direction = line.split(" ", 0)[1]
        ip = line.split(" ", 1)[2]
        port = line.split(" ", 2)[3]
        flag = line.split(" ", 3)[4]

        # time to accept, reject, or drop
        decision = firewall(rules, direction, ip, port, flag)
        if decision == "drop":
            # do the drop output
        else:
            # if decision is a number, then it's action from line

f.close()















#
