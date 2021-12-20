import socket
import threading
from tracker import Tracker

host, port = "0.0.0.0", 23456
tracker = Tracker("42")

class ConnectionThread(threading.Thread):
    def __init__(self, name, cli_socket, cli_addr):
        threading.Thread.__init__(self)
        self.name = name
        self.cli_socket = cli_socket
        self.cli_addr = cli_addr

    def run(self):
        print(f"Starting {self.name}...")

        self.cli_socket.send(f"HE::{tracker.uuid}".encode())
        #TODO is_registered = False

        while True:
            request = self.cli_socket.recv(1024).decode().strip()
            request_type = request.split("::")[0]

            if request_type == "IG":
                self.cli_socket.send(f"OG::{tracker.uuid}".encode())
            elif request_type == "QU":
                self.cli_socket.send("BY".encode())
                self.cli_socket.close()
                break
            elif request_type == "RG":
                response = tracker.register(request)
                self.cli_socket.send(response.encode())
            elif request_type == "CS":
                peers = tracker.get_peers()

                self.cli_socket.send("CO::BEGIN".encode())
                for peer in peers:
                    self.cli_socket.send(peer.to_string(prefix="CO").encode())
                self.cli_socket.send("CO::END".encode())

        print(f"Ending {self.name}...")    

def main():
    all_threads = []

    with socket.socket() as s_socket:
        s_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s_socket.bind((host, port))
        s_socket.listen(0)
        s_socket.settimeout(1)

        print("Listening...")
        while True:
            try:
                c_soc, c_addr = s_socket.accept()
                new_thread = ConnectionThread(f"Thread{len(all_threads)}", c_soc, c_addr)
                all_threads.append(new_thread)
                new_thread.start()

            except socket.timeout:
                continue
            except KeyboardInterrupt:
                for thread in all_threads:
                    thread.join()
                return

        for thread in all_threads:
            thread.join()

if __name__ == "__main__":
    main()
