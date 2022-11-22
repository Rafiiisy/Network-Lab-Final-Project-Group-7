import socket
import threading
import pickle
import sys
import subprocess

cond = {}

def serverListen(serverSocket):
    while True:
        msg = serverSocket.recv(1024).decode("utf-8")
        if msg == "/viewRequests":
            serverSocket.send(bytes(".","utf-8"))
            response = serverSocket.recv(1024).decode("utf-8")
            if response == "/sendingData":
                serverSocket.send(b"/readyForData")
                data = pickle.loads(serverSocket.recv(1024))
                if data == set():
                    print("No pending requests.")
                else:
                    print("Pending Requests:")
                    for element in data:
                        print(element)
            else:
                print(response)
        elif msg == "/approveRequest":
            serverSocket.send(bytes(".","utf-8"))
            response = serverSocket.recv(1024).decode("utf-8")
            if response == "/proceed":
                cond["inputMsg"] = False
                print("Enter the username to approve: ")
                with cond["inputCondt"]:
                    cond["inputCondt"].wait()
                cond["inputMsg"] = True
                serverSocket.send(bytes(cond["userInput"],"utf-8"))
                print(serverSocket.recv(1024).decode("utf-8"))
            else:
                print(response)
        elif msg == "/messageSend":
            serverSocket.send(bytes(cond["userInput"],"utf-8"))
            cond["sendMessageLock"].release()
        elif msg == "/allMembers":
            serverSocket.send(bytes(".","utf-8"))
            data = pickle.loads(serverSocket.recv(1024))
            print("All group members:")
            for element in data:
                print(element)
        elif msg == "/onlineMembers":
            serverSocket.send(bytes(".","utf-8"))
            data = pickle.loads(serverSocket.recv(1024))
            print("Online group members:")
            for element in data:
                print(element)
        elif msg == "/changeAdmin":
            serverSocket.send(bytes(".","utf-8"))
            response = serverSocket.recv(1024).decode("utf-8")
            if response == "/proceed":
                cond["inputMsg"] = False
                print("Enter username of the new admin: ")
                with cond["inputCondt"]:
                    cond["inputCondt"].wait()
                cond["inputMsg"] = True
                serverSocket.send(bytes(cond["userInput"],"utf-8"))
                print(serverSocket.recv(1024).decode("utf-8"))
            else:
                print(response)
        elif msg == "/whoAdmin":
            serverSocket.send(bytes(cond["groupname"],"utf-8"))
            print(serverSocket.recv(1024).decode("utf-8"))
        elif msg == "/kickMember":
            serverSocket.send(bytes(".","utf-8"))
            response = serverSocket.recv(1024).decode("utf-8")
            if response == "/proceed":
                cond["inputMsg"] = False
                print("Who do you want to kick? ")
                with cond["inputCondt"]:
                    cond["inputCondt"].wait()
                cond["inputMsg"] = True
                serverSocket.send(bytes(cond["userInput"],"utf-8"))
                print(serverSocket.recv(1024).decode("utf-8"))
            else:
                print(response)    
        elif msg == "/kicked":
            cond["connected"] = False
            cond["inputMsg"] = False
            print("You have been kicked :( Press any key to quit.")
            break
        elif msg == "/fileTransfer":
            cond["inputMsg"] = False
            print("Please enter the filename: ")
            with cond["inputCondt"]:
                cond["inputCondt"].wait()
            cond["inputMsg"] = True
            filename = cond["userInput"]
            try:
                f = open(filename,'rb')
                f.close()
            except FileNotFoundError:
                print("The requested file does not exist.")
                serverSocket.send(bytes("~error~","utf-8"))
                continue
            serverSocket.send(bytes(filename,"utf-8"))
            serverSocket.recv(1024)
            print("Uploading file to server...")
            with open(filename,'rb') as f:
                data = f.read()
                dataLen = len(data)
                serverSocket.send(dataLen.to_bytes(4,'big'))
                serverSocket.send(data)
            print(serverSocket.recv(1024).decode("utf-8"))
        elif msg == "/receiveFile":
            print("Receiving shared group file...")
            serverSocket.send(b"/sendFilename")
            filename = serverSocket.recv(1024).decode("utf-8")
            serverSocket.send(b"/sendFile")
            remaining = int.from_bytes(serverSocket.recv(4),'big')
            f = open(filename,"wb")
            while remaining:
                data = serverSocket.recv(min(remaining,4096))
                remaining -= len(data)
                f.write(data)
            f.close()
            print("Received file saved as",filename)
        elif msg == "/PlayRPS":
                serverSocket.send(b"/JoinRPS")
                serverSocket.recv(1024).decode("utf-8")
                # CHANGE FILE DIRECTORY , KEEP '&& PYTHON GAMESERVER.PY
                cmd = 'cd/Users/Dell/Documents/final_project && python gameserver.py'
                p1 = subprocess.run(cmd, shell=True)
                p1.returncode
                if msg == "OK":
                    # CHANGE FILE DIRECTORY , KEEP '&& PYTHON GAMECLIENT.PY
                    cmd = 'cd/Users/Dell/Documents/final_project && python gameclient.py'
                    p2 = subprocess.run(cmd, shell=True)
                    p2.returncode
                elif msg == "Q":
                    serverSocket.send(b"/JoinRPS")
                    serverSocket.recv(1024).decode("utf-8")
                    p1.kill()
        elif msg == "/JoinRPS":
                serverSocket.send(b"/JoinRPS")
                serverSocket.recv(1024).decode("utf-8")
                # CHANGE FILE DIRECTORY , KEEP '&& PYTHON GAMECLIENT.PY
                cmd = 'cd/Users/Dell/Documents/final_project && python gameclient.py'
                p2 = subprocess.run(cmd, shell=True)
                p2.returncode
                if msg == "Q":
                    serverSocket.send(b"/JoinRPS")
                    serverSocket.recv(1024).decode("utf-8")
                    p2.kill()
                
            # cmd2 = 'python gameClient.py'
            # p2 = subprocess.Popen(cmd2, shell=True)
            # out, err = p2.communicate()
            # print(err)
            # print(out)
        else:
            print(msg)     

def userInput(serverSocket):
    while cond["connected"]:
        cond["sendMessageLock"].acquire()
        cond["userInput"] = input()
        cond["sendMessageLock"].release()
        with cond["inputCondt"]:
            cond["inputCondt"].notify()
        if cond["userInput"] == "/view":
            serverSocket.send(b"/viewRequests")
        elif cond["userInput"] == "/approve":
            serverSocket.send(b"/approveRequest")
        elif cond["userInput"] == "/exit":
            serverSocket.send(b"/disconnect")
            break
        elif cond["userInput"] == "/members":
            serverSocket.send(b"/allMembers")
        elif cond["userInput"] == "/online":
            serverSocket.send(b"/onlineMembers")
        elif cond["userInput"] == "/changeAdmin":
            serverSocket.send(b"/changeAdmin")
        elif cond["userInput"] == "/Admin":
            serverSocket.send(b"/whoAdmin")
        elif cond["userInput"] == "/kick":
            serverSocket.send(b"/kickMember")
        elif cond["userInput"] == "/file":
            serverSocket.send(b"/fileTransfer")
        elif cond["userInput"] == "/play":
            serverSocket.send(b"/PlayRPS")
        elif cond["userInput"] == "/join":
            serverSocket.send(b"/JoinRPS")
        elif cond["inputMsg"]:
            cond["sendMessageLock"].acquire()
            serverSocket.send(b"/messageSend")

def waitServerListen(serverSocket):
    while not cond["connected"]:
        msg = serverSocket.recv(1024).decode("utf-8")
        if msg == "/accepted":
            cond["connected"] = True
            print("Your join request has been approved. Press any key to begin chatting!")
            break
        elif msg == "/waitDisconnect":
            cond["joinDisconnect"] = True
            break

def waitUserInput(serverSocket):
    while not cond["connected"]:
        cond["userInput"] = input()
        if cond["userInput"] == "/1" and not cond["connected"]:
            serverSocket.send(b"/waitDisconnect")
            break

def main():
    if len(sys.argv) < 3:
        print("FORMAT: python client.py <IP> <Port>")
        print("EXAMPLE: python client.py localhost 8000")
        return
    serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    serverSocket.connect((sys.argv[1], int(sys.argv[2])))
    #serverSocket.bind(("172.16.110.92", 1500))
    cond["inputCondt"] = threading.Condition()
    cond["sendMessageLock"] = threading.Lock()
    cond["username"] = input("Welcome! Please enter your username: ")
    cond["groupname"] = input("Enter the name of your group: ")
    cond["connected"] = False
    cond["joinDisconnect"] = False
    cond["inputMsg"] = True
    serverSocket.send(bytes(cond["username"],"utf-8"))
    serverSocket.recv(1024)
    serverSocket.send(bytes(cond["groupname"],"utf-8"))
    response = serverSocket.recv(1024).decode("utf-8")
    if response == "/adminReady":
        print("You have created the group",cond["groupname"],"and are now an admin.")
        cond["connected"] = True
    elif response == "/ready":
        print("You have joined the group",cond["groupname"])
        cond["connected"] = True
    elif response == "/wait":
        print("Your request to join the group is pending for admin approval.")
        print("Available Commands:\n/1 -> Disconnect\n")
    waitUserInputThread = threading.Thread(target=waitUserInput,args=(serverSocket,))
    waitServerListenThread = threading.Thread(target=waitServerListen,args=(serverSocket,))
    userInputThread = threading.Thread(target=userInput,args=(serverSocket,))
    serverListenThread = threading.Thread(target=serverListen,args=(serverSocket,))
    waitUserInputThread.start()
    waitServerListenThread.start()
    while True:
        if cond["connected"] or cond["joinDisconnect"]:
            break
    if cond["connected"]:
        print("Available Commands:\n/view: View Join Requests (Admins)\n/approve: Approve Join Requests (Admin)\n/exit: Disconnect\n/members: View All Members\n/online: View Online Group Members\n/changeAdmin: Change admin of the group\n/Admin: Check Group Admin\n/kick: Kick Member\n/file: File Transfer\n/play: Play Rock Paper Scissor \n/join: Join Rock Paper Scissor\nType anything else to send a message")
        waitUserInputThread.join()
        waitServerListenThread.join()
        userInputThread.start()
        serverListenThread.start()
    while True:
        if cond["joinDisconnect"]:
            serverSocket.shutdown(socket.SHUT_RDWR)
            serverSocket.close()
            waitUserInputThread.join()
            waitServerListenThread.join()
            print("Disconnected. Good bye :(")
            break
        elif not cond["connected"]:
            serverSocket.shutdown(socket.SHUT_RDWR)
            serverSocket.close()
            userInputThread.join()
            serverListenThread.join()
            print("Disconnected. Good bye :(")
            break

if __name__ == "__main__":
    main()