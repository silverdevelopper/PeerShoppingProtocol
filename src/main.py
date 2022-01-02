import logging
import os
import socket
import uuid
import sys
from peer import Peer
from client_connection import PeerConnectionThread, TrackerConnectionThread
from tracker import Tracker
from pathlib import Path

host, port = "0.0.0.0", 23456

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
    tracker = Tracker(uuid.uuid4(), host, port, geoloc="Istanbul")
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
                new_thread = TrackerConnectionThread(
                    tracker, client_socket, client_address
                )
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
    if len(sys.argv) == 1:
        info()
        return
    elif sys.argv[1] == "-t":
        start_tracker()
    elif sys.argv[1] == "-a":
        start_intelligent_home()


def start_intelligent_home():
    if len(sys.argv) != 4:
        info()
        raise Exception("Command line expect tracker ip and port")
    # TODO: implement intelligent home

    all_threads = []
    port = int(sys.argv[3])
    host = sys.argv[2]
    peer = Peer(uuid.uuid4(), host, port, geoloc="Istanbul")

    with socket.socket() as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(0)
        server_socket.settimeout(1)

        print("Listening...")

        while True:
            try:
                (client_socket, client_address) = server_socket.accept()
                logging.info(f"New connection from IP:{client_address[0]}")

                connected_peer_info = peer.get_peer_by_address(client_address)

                # TODO handle peer not found
                if not connected_peer_info:
                    print("Unknown peer")
                    print("TODO should fetch peers from a tracker on startup")
                    client_socket.send("ER".encode())
                    client_socket.close()
                    continue

                new_thread = PeerConnectionThread(
                    peer, connected_peer_info, client_socket, client_address
                )
                all_threads.append(new_thread)
                new_thread.start()

            except socket.timeout:
                continue
            except KeyboardInterrupt:
                for thread in all_threads:
                    thread.join()

                logging.debug("Tracker shutting down...")
                return


# To start Peer use -a command line
def info():
    print(
        "Arguments: [node option] [connection option]",
        "node option for peer:  -a , connection option: {ip} {port}",
        "node option for tracker: -t",
        sep="\n",
    )


if __name__ == "__main__":
    main()
