import socket
from tracker import Tracker
from client_connection import ConnectionThread

host, port = "0.0.0.0", 23456
tracker = Tracker("42")


def main():
    all_threads = []

    with socket.socket() as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(0)
        server_socket.settimeout(1)

        print("Listening...")
        while True:
            try:
                (client_socket,) = server_socket.accept()
                new_thread = ConnectionThread(tracker, client_socket)
                all_threads.append(new_thread)
                new_thread.start()

            except socket.timeout:
                continue
            except KeyboardInterrupt:
                for thread in all_threads:
                    thread.join()
                return


if __name__ == "__main__":
    main()
