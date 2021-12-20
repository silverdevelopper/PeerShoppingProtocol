import socket

from tracker import Tracker

host, port = "0.0.0.0", 23456
tracker = Tracker("42")


def main():

    with socket.socket() as l_socket:
        l_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        l_socket.bind((host, port))
        l_socket.listen(0)
        l_socket.settimeout(1)

        print("Listening...")
        while True:
            try:
                # TODO this should run on a separate thread
                c_soc, c_addr = l_socket.accept()

                c_soc.send(f"HE::{tracker.uuid}".encode())

                while True:
                    request = c_soc.recv(1024).decode().strip()
                    request_type = request.split("::")[0]

                    if request_type == "IG":
                        c_soc.send(f"OG::{tracker.uuid}".encode())
                    elif request_type == "QU":
                        c_soc.send("BY".encode())
                        c_soc.close()
                        break
                    elif request_type == "RG":
                        response = tracker.register(request)
                        c_soc.send(response.encode())
                    elif request_type == "CS":
                        peers = tracker.get_peers()

                        c_soc.send("CO::BEGIN".encode())
                        for peer in peers:
                            c_soc.send(peer.to_string(prefix="CO").encode())
                        c_soc.send("CO::END".encode())

            except socket.timeout:
                continue


if __name__ == "__main__":
    main()
