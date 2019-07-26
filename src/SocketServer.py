import socket
import select
fd_to_socket = {}
READ_ONLY = ( select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR)
READ_WRITE = (READ_ONLY|select.POLLOUT)
poller = select.poll()
server = None
IP = '127.0.0.1'
Port = 7002

def getAddress ():
    return IP, Port

def initServer(ip=IP, port=Port):
    global server
    global IP
    global Port
    IP = ip
    Port = port
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(False)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = (ip, port)
        
        server.bind(server_address)
        server.listen(1)
        
        poller.register(server,READ_ONLY)
        global fd_to_socket
        fd_to_socket = {server.fileno():server,}
    except Exception as e:
        print (e)
        return False
    return True
   
def isTimeout(events):
    return (events == None or len(events) == 0)
    
def runServer(timeout, timeoutFn, recivedFn):
    global fd_to_socket
    isFirstTime = True
    sumTimeoutTimes = 0
    while True:
        events = poller.poll(500)
        
        if (isTimeout(events)):
            sumTimeoutTimes += 1
            if (isFirstTime or sumTimeoutTimes * 500 >= timeout):
                isFirstTime = False
                sumTimeoutTimes = 0
                timeoutFn()
                pass
            continue # if (isTimeout(events)):
        
        for fd, flag in events: 
            if flag & (select.POLLIN | select.POLLPRI) :
                s = fd_to_socket[fd]
                if s is server :
                    connection , client_address = s.accept()
                    connection.setblocking(False)
                    fd_to_socket[connection.fileno()] = connection
                    poller.register(connection,READ_ONLY)
                elif(s):
                    result = s.recv(1024)
                    poller.unregister(s)
                    fd_to_socket.pop(fd)
                    s.close()
                    recivedFn(result)
                else:
                    fd_to_socket.pop(fd)
                    pass
                pass # if flag & (select.POLLIN | select.POLLPRI)
        pass # while