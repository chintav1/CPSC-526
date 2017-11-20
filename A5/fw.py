import sys, os
import select



def bitmask(r_ip, p_ip):

    # if rule has '*', then any ip is accepted so return as accepted
    if r_ip == "*":
        return True

    # get and separate ip from rule
    # check for bad ip
    ip = r_ip.split("/", 1)[0]
    try:
        r_bits = int(r_ip.split("/", 2)[1])
    except:
        print("Error: bad rule IP input. Continuing...", file=sys.stderr)
        return False

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
    mask = 0b0
    mask1 = 0
    mask2 = 0
    mask3 = 0
    mask4 = 0

    # get rules' ip and packet's ip into bit-format, and compare through that
    for i in range(1,r_bits+1):
        # restart ever 8 bits
        if (i == 9 or i == 17  or i == 25):
            mask = 0b0
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

    # prepare to compare ip's
    # use mask and packet's ip's
    ip1 = mask1 & p_ip1
    ip2 = mask2 & p_ip2
    ip3 = mask3 & p_ip3
    ip4 = mask4 & p_ip4

    # use mask and rules' ip's
    r_ip1 = mask1 & r_ip1
    r_ip2 = mask2 & r_ip2
    r_ip3 = mask3 & r_ip3
    r_ip4 = mask4 & r_ip4

    if ip1==r_ip1 and ip2==r_ip2 and ip3==r_ip3 and ip4==r_ip4:
        return True
    else:
        return False


def get_ports(r_port, port):
    # if no comma, no ports to be separated
    if "," not in r_port or r_port == "*":
        return r_port

    # if multiple ports listed, check each one
    ports = r_port.split(",")
    for p in ports:
        if p == port:
            return p

    # if it reaches here, then none of the ports match
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
        if DEBUG: print("port:", rules[i][4], port, "match:", port_match)

        # check if established connection
        # turn the flag into an int and check
        try:
            f = int(flag)
        except:
            print("Error: incorrect packet format. Exiting...")
            sys.exit(1)

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
        if d_match == 1 and ip_match == 1 and port_match == 1 and establish == 1:
            return str(rules[i][0]) + " " + rules[i][2]

    # if reaches here, then no rules for this packet, so reject
    return "drop"


#################
##### Rules #####
#################

rules = [[]]
linenum = 0
flag = ""
config_file = ""

# some input error checking first
if len(sys.argv) == 2:
    config_file = sys.argv[1]
else:
    print("Error: incorrect amount of arguments supplied. Exiting...", file=sys.stderr)
    sys.exit(1)
if not (os.path.exists(config_file) and os.path.isfile(config_file)):
    print("Error: \"",config_file,"\" does not exist or is not a file. Exiting...", file=sys.stderr)
    sys.exit(1)
if not config_file.lower().endswith(".txt"):
    print("Error: file must be .txt type. Exiting...", file=sys.stderr)
    sys.exit(1)

with open(config_file, "r") as f:
    for line in f:
        # split string to be put into a list
        line = line.replace("\n", "")
        line.strip("\t")
        line = " ".join(line.split())

        # ignore empty lines or comments, but increment line number
        if len(line) == 0 or line[0] == "#":
            linenum = linenum + 1
            continue

        try:
            direction = line.split(" ", 1)[0]
            action = line.split(" ", 2)[1]
            ip = line.split(" ", 3)[2]
            port = line.split(" ", 4)[3]
        except:
            print("Error: rules are written weird. Continuing...", file=sys.stderr)
            continue
        if len(line.split(" ")) == 5:
            flag = line.split(" ", 5)[4]
        else:
            flag = ""
        if linenum == 0:
            rules[linenum] = [linenum+1, direction, action, str(ip), str(port), flag]
        else:
            rules.append([linenum+1, direction, action, str(ip), str(port), flag])
        linenum = linenum + 1
f.close()



###################
##### Packets #####
###################

# direction, ip, port, flag
packet = ["", "", "", ""]

# first check if anything in standard output
if not select.select([sys.stdin,],[],[],0.0)[0]:
    print("Error: I need some file through standard input to work with. Exiting...", file=sys.stderr)
    sys.exit(1)
try:
    for line in sys.stdin:
        # clean up the list, then separate
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
            result = "drop() "+direction+" "+ip+" "+port+" "+flag
            print(result.rstrip(), file = sys.stdout)
        else:
            # if doesn't say drop, then do action
            linenum = decision.split(" ", 1)[0]
            action = decision.split(" ", 2)[1]
            result = action+"("+linenum+") "+direction+" "+ip+" "+port+" "+flag
            print(result.rstrip(), file = sys.stdout)
except:
    print("Error: unable to comprehend file. Exiting...", file=sys.stderr)
    sys.exit(1)
















#
