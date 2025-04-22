import socket
import threading

HOST = '0.0.0.0'
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = {}  # maps client socket to client name
print(f"Server listening on {HOST}:{PORT}")

def recv_exact(sock, num_bytes):
    data = b""
    while len(data) < num_bytes:
        chunk = sock.recv(num_bytes - len(data))
        if not chunk:
            raise ConnectionError("Socket closed before receiving expected bytes")
        data += chunk
    return data

def broadcast(message, source_client=None):
    for client in list(clients):
        if client != source_client:
            try:
                client.send("__send_texts__".encode())
                client.send(message.encode())
            except:
                client.close()
                clients.pop(client, None)

def handle_client(client):
    try:
        name = client.recv(1024).decode()
        clients[client] = name
        print(f"{name} has joined the chat.")
        broadcast(f"{name} has joined the chat.", client)

        while True:
            try:
                header = ''
                header = client.recv(14)
                if not header:
                    break

                header_str = header.decode()

                if header_str.startswith("__send_files__"):
                    filename_len = int(recv_exact(client, 4).decode())
                    filename = recv_exact(client, filename_len).decode()
                    filesize = int(recv_exact(client, 16).decode())

                    file_data = recv_exact(client, filesize)

                    for c in list(clients):
                        if c != client:
                            try:
                                c.send("__send_files__".encode())
                                c.send(f"{len(filename):04d}".encode())
                                c.send(filename.encode())
                                c.send(f"{filesize:016d}".encode())
                                c.sendall(file_data)
                            except:
                                c.close()
                                clients.pop(c, None)

                elif header_str.startswith("__send_video__"):
                    filename_len = int(recv_exact(client, 4).decode())
                    filename = recv_exact(client, filename_len).decode()
                    filesize = int(recv_exact(client, 16).decode())

                    video_data = recv_exact(client, filesize)

                    for c in list(clients):
                        if c != client:
                            try:
                                c.send("__send_video__".encode())
                                c.send(f"{len(filename):04d}".encode())
                                c.send(filename.encode())
                                c.send(f"{filesize:016d}".encode())
                                c.sendall(video_data)
                            except:
                                c.close()
                                clients.pop(c, None)

                elif header_str.startswith("__send_texts__"):
                    message = ''
                    message = client.recv(4096).decode()
                    #sender_name = clients.get(client, "Unknown")
                    broadcast(message,client)

            except Exception as e:
                print(f"Error during message processing: {e}")
                break
            
    except Exception as e:
        print(f"Error with client: {e}")
    finally:
        name = clients.get(client, "A user")
        print(f"{name} has left the chat.")
        broadcast(f"{name} has left the chat.", client)
        client.close()
        clients.pop(client, None)

def receive_connections():
    while True:
        client, address = server.accept()
        print(f"Connected with {address}")
        threading.Thread(target=handle_client, args=(client,), daemon=True).start()

receive_connections()
