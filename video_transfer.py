import os
def send_video(client_socket, file_path):
    try:
        filename = os.path.basename(file_path)
        filesize = os.path.getsize(file_path)

        # Send a header to notify this is a video
        client_socket.send("__send_video__".encode())
        client_socket.send(f"{len(filename):04d}".encode())  # 4-digit filename length
        client_socket.send(filename.encode())
        client_socket.send(f"{filesize:016d}".encode())      # 16-digit file size

        # Send file data in chunks
        with open(file_path, 'rb') as file:
            while True:
                chunk = file.read(4096)
                if not chunk:
                    break
                client_socket.sendall(chunk)

        print(f"Video '{filename}' sent successfully.")

    except Exception as e:
        print("Video send error:", e)
        
def recv_exact(sock, num_bytes):
    data = b""
    while len(data) < num_bytes:
        packet = sock.recv(num_bytes - len(data))
        if not packet:
            raise ConnectionError("Socket closed before expected data was received")
        data += packet
    return data

def receive_video(sock, save_directory):
    try:
        # 1. Receive filename length
        filename_len = int(recv_exact(sock, 4).decode())

        # 2. Receive filename
        filename = recv_exact(sock, filename_len).decode()

        # 3. Receive filesize
        filesize = int(recv_exact(sock, 16).decode())

        # 4. Prepare file path
        save_path = os.path.join(save_directory, filename)

        # 5. Receive the video content
        with open(save_path, "wb") as f:
            remaining = filesize
            while remaining > 0:
                chunk_size = min(4096, remaining)
                chunk = sock.recv(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                remaining -= len(chunk)

        print(f"Video received and saved to: {save_path}")

    except Exception as e:
        print("Video receive error:", e)
