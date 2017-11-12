import sys, os
import subprocess




# choose ciphers
times = 0

for i in range(0, 3):
    if i == 0:
        cipher = "null"
    elif i == 1:
        cipher = "aes128"
    else:
        cipher = "aes256"

    # choose size of file
    for j in range(0, 3):
        if j == 0:
            size = "1K"
        elif j == 1:
            size = "1M"
        else:
            size = "1G"
        # choose read or write
        for k in range(0, 2):
            if k == 0:
                command = "write"
            else:
                command = "read"
            #print(cipher +" "+ size +" "+ command)

                #shellInput = "time dd if=/dev/urandom bs="+size+" iflag=fullblock count=1 > "+size+"B.bin | python3 client.py "+command+" "+size+"B.bin 136.159.5.27:9999 "+cipher+" secretkey123"
                #result = subprocess.call([shellInput], shell=True, executable="bash")

result = ""
with open("log.txt", "r") as f:
    for line in f:
        if "real" in line:
            result = result + "\n" + line.split("\t",2)[1]
f.close()

line = result.split()



filename = ""
lineRange = 0

for i in range(0, 3):
    if i == 0:
        cipher = "null"
    elif i == 1:
        cipher = "aes128"
    else:
        cipher = "aes256"

    # choose size of file
    for j in range(0, 3):
        if j == 0:
            size = "1K"
        elif j == 1:
            size = "1M"
        else:
            size = "1G"
        # choose read or write
        for k in range(0, 2):
            if k == 0:
                command = "write"
            else:
                command = "read"
            filename = cipher+"-"+size+"-"+command+".txt"
            with open(filename, "w") as f:
                output = line[lineRange:(lineRange+10)]
                output = [s.replace("m", "") for s in output]
                output = "\n".join([s.replace("s", "") for s in output])
                f.write(output)
            f.close()
            print(filename)
            print(output)
            lineRange = lineRange + 10
