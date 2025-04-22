import os
def send_file(client_socket, file_path):
    try:
        filename = os.path.basename(file_path)
        filesize = os.path.getsize(file_path)

        # Notify server it's a file
        client_socket.send("__send_files__".encode())
        client_socket.send(f"{len(filename):04d}".encode())  # 4-digit filename length
        client_socket.send(filename.encode())
        client_socket.send(f"{filesize:016d}".encode())      # 16-digit file size

        # Send file data in chunks (binary)
        with open(file_path, "rb") as file:
            while True:
                chunk = file.read(4096)
                if not chunk:
                    break
                client_socket.sendall(chunk)

        print(f"File '{filename}' sent successfully.")

    except Exception as e:
        print(f"Error while sending file: {e}")
def recv_exact(sock, num_bytes):
    data = b""
    while len(data) < num_bytes:
        packet = sock.recv(num_bytes - len(data))
        if not packet:
            raise ConnectionError("Socket closed before receiving expected bytes")
        data += packet
    return data

def receive_file(sock, save_directory):
    try:
        filename_len = int(recv_exact(sock, 4).decode())
        filename = recv_exact(sock, filename_len).decode()
        filesize = int(recv_exact(sock, 16).decode())

        save_path = os.path.join(save_directory, filename)
        with open(save_path, "wb") as f:
            remaining = filesize
            while remaining > 0:
                chunk = sock.recv(min(4096, remaining))
                if not chunk:
                    break
                f.write(chunk)
                remaining -= len(chunk)

        print(f"File received and saved to: {save_path}")

    except Exception as e:
        print(f"Error receiving file: {e}")
