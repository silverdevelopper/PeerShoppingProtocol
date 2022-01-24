import logging
import os
import socket
import sys
import threading
from client_connection import PeerConnectionThread, TrackerConnectionThread
from pathlib import Path
from db_operations import DataBase
from models.peer_info import PeerInfo
from peer import Peer
from models.product import Product
from tracker import Tracker
from uuid import uuid4

HOST, PORT = "0.0.0.0", 23456
killswitch = False

current_path = str(Path(__file__))
log_dir = os.path.join(os.path.normpath(current_path + os.sep + os.pardir), "logs")
log_fname = os.path.join(log_dir, "tracker.log")
os.makedirs(os.path.dirname(log_fname), exist_ok=True)
logging.basicConfig(
    filename=log_fname,
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.DEBUG,
)


def start_tracker():
    global killswitch
    tracker = Tracker(uuid4(), HOST, PORT, geoloc="Istanbul")
    all_threads = []

    with socket.socket() as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(0)
        # server_socket.settimeout(10)

        logging.debug("Tracker starting up...")
        print("racker starting up...")
        print("Listening...")
        while True:
            try:
                (client_socket, client_address) = server_socket.accept()
                logging.info(f"New connection from IP:{client_address[0]}")
                client_socket.settimeout(0.8)
                new_thread = TrackerConnectionThread(
                    tracker, client_socket, client_address
                )
                all_threads.append(new_thread)
                new_thread.start()

                if killswitch:
                    break

            except socket.timeout:
                #print("Timeout! Tracker shutting down...", e)
                #logging.debug("Timeout! Tracker shutting down...")
                #return
                if killswitch:
                    break
                else:
                    continue
            except KeyboardInterrupt:
                for thread in all_threads:
                    thread.join()

                logging.debug("Tracker shutting down...")
                return


peer = None
def start_intelligent_home():
    global peer
    global killswitch
    if len(sys.argv) != 4:
        info()
        raise Exception("Command line expect tracker ip and port")

    all_threads = []
    port = int(sys.argv[3])
    host = sys.argv[2]
    dbname = "mydb"
    
    if len(sys.argv) == 5:
        dbname = sys.argv[4]

    peer = Peer(uuid4(), host, port, geoloc="Istanbul")
    
    db = DataBase(db_name=dbname)
    for raw_peer_info in db.read_peers_as_list():
        name,uuid,ip,port,desc,location = raw_peer_info
        peer_info = PeerInfo(uuid,ip,port,location,"A",keywords=name+desc)
        peer.register(peer_info)

    for product_info in db.read_products_as_list():
        p_name, p_unit, p_desc, p_amount = product_info
        keywords = [kw.strip().lower() for kw in p_desc.split(",")]
        new_product = Product(p_name, p_unit, p_amount, keywords)
        peer.add_product(new_product)

    with socket.socket() as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(0)
        server_socket.settimeout(1)
        print("Listening...")

        while True:
            try:
                (client_socket, client_address) = server_socket.accept()
                #client_socket.settimeout(0.8)

                if client_address in peer.block_list:
                    client_socket.send("BL::T\n".encode())
                    client_socket.close()
                    logging.info(f"Rejeted connection from blocked IP:{client_address[0]}")
                    continue

                logging.info(f"New connection from IP:{client_address[0]}")

                new_thread = PeerConnectionThread(peer, client_socket, client_address)
                all_threads.append(new_thread)
                new_thread.start()

                if killswitch:
                    break

            except socket.timeout as e:
                if killswitch:
                    break
                else:
                    continue
            except KeyboardInterrupt:
                for thread in all_threads:
                    thread.join()

                logging.debug("Tracker shutting down...")
                return
        
        for thread in all_threads:
            thread.is_listening = False
            thread.join()

# To start Peer use -a command line
def info():
    print(
        "Arguments: [node option] [connection option]",
        "node option for peer:  -a , connection option: {ip} {port}",
        "node option for tracker: -t",
        sep="\n",
    )


def main():
    global killswitch
    if len(sys.argv) == 1:
        info()
        return
    elif sys.argv[1] == "-t":
        start_tracker()
    elif sys.argv[1] == "-a":
        peer_thread = threading.Thread(target=start_intelligent_home)
        peer_thread.start()
        
        from app import AppUi
        while peer is None: 
            pass
        app_ui = AppUi(peer)
        app_ui.run()

        killswitch = True
        peer_thread.join()


if __name__ == "__main__":
    main()
