# berkeley_server.py
import socket
import time
import threading

client_sockets = []
client_times = []
lock = threading.Lock()
connection_window = 120  # seconds to wait for clients

def handle_client(conn, addr):
    try:
        client_time = float(conn.recv(1024).decode())
        readable_client_time = time.strftime('%H:%M', time.localtime(client_time))
        print(f"[{addr}] Reported time: {readable_client_time}")
        with lock:
            client_sockets.append(conn)
            client_times.append(client_time)
    except:
        conn.close()

def start_server():
    host = '127.0.0.1'  # Accept connections from other machines
    port = 8080
    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(5)

    print("Server started. Waiting for clients to connect...\n")

    start_time = time.time()
    threads = []

    while time.time() - start_time < connection_window:
        server_socket.settimeout(connection_window - (time.time() - start_time))
        try:
            conn, addr = server_socket.accept()
            print(f"Client connected from {addr}")
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            threads.append(thread)
        except socket.timeout:
            break

    for t in threads:
        t.join()

    if not client_sockets:
        print("No clients connected. Exiting.")
        return

    master_time = time.time()
    readable_master_time = time.strftime('%H:%M', time.localtime(master_time))
    print(f"\nServer (Master) current time: {readable_master_time}")

    with lock:
        client_times.append(master_time)

    average_time = sum(client_times) / len(client_times)
    readable_avg_time = time.strftime('%H:%M', time.localtime(average_time))
    print(f"Calculated synchronized time: {readable_avg_time}")

    # Send synchronized time to all clients
    for conn in client_sockets:
        try:
            conn.send(str(average_time).encode())
            conn.close()
        except:
            continue

    print("Synchronized time sent to all clients. Server done.")

if __name__ == '__main__':
    start_server()


# *******************************************************************************************************************************



# berkeley_client.py
import socket
import time
import random

def start_client():
    server_ip = '127.0.0.1'  # Replace with actual IP of server machine
    port = 8080

    client_socket = socket.socket()
    client_socket.connect((server_ip, port))

    # Simulate a clock with skew: +/- 5 seconds
    local_time = time.time() + random.uniform(-5, 5)
    readable_local_time = time.strftime('%H:%M', time.localtime(local_time))
    print(f"Client local time before sync: {readable_local_time}")
    client_socket.send(str(local_time).encode())

    # Receive synchronized time from server
    sync_time = float(client_socket.recv(1024).decode())
    readable_sync_time = time.strftime('%H:%M', time.localtime(sync_time))
    print(f"Synchronized time received: {readable_sync_time}")

    client_socket.close()

if __name__ == '__main__':
    start_client()





