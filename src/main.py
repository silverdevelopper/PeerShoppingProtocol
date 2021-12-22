import logging
import os
import socket
import uuid
from client_connection import ConnectionThread
from tracker import Tracker

host, port = "0.0.0.0", 23456
tracker = Tracker(uuid.uuid4())

log_dir = os.path.join(os.path.normpath(os.getcwd() + os.sep + os.pardir), 'logs')
log_fname = os.path.join(log_dir, 'tracker.log')
os.makedirs(os.path.dirname(log_fname), exist_ok=True)
logging.basicConfig(filename=log_fname, filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)

def main():
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


if __name__ == "__main__":
    main()
