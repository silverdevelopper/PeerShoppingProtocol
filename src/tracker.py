import socket
import threading

def main():
    host, port = "0.0.0.0", 23456

    all_threads = []
    
    with socket.socket() as l_socket:
        l_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        l_socket.bind((host, port))
        l_socket.listen(0)
        l_socket.settimeout(1)

        thread_num = 0

        print("SERVER IS STARTING...")
        while True:
            try:
                c_soc, c_addr = l_socket.accept()
                print("A NEW CLIENT HAS CONNECTED: ", c_addr)
                c_soc.settimeout(.8)

                
                thread_num += 1
            except socket.timeout:
                continue
        
        for thread in all_threads:
            thread.join()

if __name__ == '__main__':
    main()