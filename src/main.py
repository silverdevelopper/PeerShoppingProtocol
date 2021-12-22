import logging
import os
import socket
import uuid
from client_connection import ConnectionThread
from tracker import Tracker
import sys

host, port = "0.0.0.0", 23456
tracker = Tracker(uuid.uuid4())

log_dir = os.path.join(os.path.normpath(os.getcwd() + os.sep + os.pardir), 'logs')
log_fname = os.path.join(log_dir, 'tracker.log')
os.makedirs(os.path.dirname(log_fname), exist_ok=True)
logging.basicConfig(filename=log_fname, filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)

def start_tracker():
    all_threads = []

    with socket.socket() as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(0)
        server_socket.settimeout(1)

        logging.debug("Tracker starting up...")
        print("Listening...")
        while True:
            try:
                (client_socket, client_address) = server_socket.accept()
                logging.info(f"New connection from IP:{client_address[0]}")
                new_thread = ConnectionThread(tracker, client_socket, client_address)
                all_threads.append(new_thread)
                new_thread.start()

            except socket.timeout:
                continue
            except KeyboardInterrupt:
                for thread in all_threads:
                    thread.join()
                    
                logging.debug("Tracker shutting down...")
                return
def main():
    if sys.argv[1] == "-t":
        start_tracker()
    elif sys.argv[1] == "-a":
        start_intelligent_home()

def start_intelligent_home():
    if len(sys.argv) != 4:
        info()
        raise Exception("Command line expect tracker ip and port")
    #TODO: implement intelligent home 
    port = int(sys.argv[3])
    host = sys.argv[2]
    client = socket.socket()
    client.connect((host,port))
    p = client.getpeername()
    print(p)
    message = client.recv(port)
    print("Server: ",message.decode("UTF-8"))
    m = "RG::{uuid}::127.0.0.1::{port}::Adana::A::nur,test".format(uuid = str(uuid.uuid4()), port = 23456)
    while True:
        print("Client: ",m)
        client.send(m.encode())
        message = client.recv(port)
        print("Server: ",message.decode("UTF-8"))
        m = input('>')
        
        

# To start Peer use -a command line
def info():
    print("""
          Arguments: [node option] [connection option]
          node option for peer:  -a , connection option: {ip} {port}
            node option for tracker: -t 
          """)

if __name__ == "__main__":
    main()
