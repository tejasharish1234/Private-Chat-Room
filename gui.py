import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import socket
import threading
from file_transfer import send_file
from video_transfer import send_video

client_socket = None
client_name = ""

def send_message():
    message = message_entry.get()
    if message:
        try:
            client_socket.send("__send_texts__".encode())
            client_socket.send(f"{client_name}: {message}".encode())
            # Show message in sender's chat box
            log_chat(f"{client_name} (You): {message}")
            message_entry.delete(0, tk.END)

        except:
            messagebox.showerror("Error", "Failed to send message.")


def receive_messages():
    while True:
        try:
            msg = ''
            msg = client_socket.recv(14)
            if not msg:
                break

            decoded = msg.decode('utf-8', errors='ignore')
            print(decoded)
            if decoded.startswith("__send_files__"):
                filename_len = int(client_socket.recv(4).decode())
                filename = client_socket.recv(filename_len).decode()
                filesize = int(client_socket.recv(16).decode())
                data = b""
                while len(data) < filesize:
                    chunk = client_socket.recv(min(4096, filesize - len(data)))
                    if not chunk:
                        break
                    data += chunk

                save_path = filedialog.asksaveasfilename(initialfile=filename, defaultextension=".txt")
                if save_path:
                    with open(save_path, "wb") as f:
                        f.write(data)
                    log_chat(f"[Received file: {filename}]")

            elif decoded.startswith("__send_video__"):
                filename_len = int(client_socket.recv(4).decode())
                filename = client_socket.recv(filename_len).decode()
                filesize = int(client_socket.recv(16).decode())
                data = b""
                while len(data) < filesize:
                    chunk = client_socket.recv(min(4096, filesize - len(data)))
                    if not chunk:
                        break
                    data += chunk

                save_path = filedialog.asksaveasfilename(initialfile=filename, defaultextension=".mp4")
                if save_path:
                    with open(save_path, "wb") as f:
                        f.write(data)
                    log_chat(f"[Received video: {filename}]")

            elif decoded.startswith("__send_texts__"):
                # Handle regular message
                message = ''
                message = client_socket.recv(4096).decode(errors='ignore')
                log_chat(message)

        except Exception as e:
            print("Receive error:", e)
            break

def log_chat(message):
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, f'{message}\n')
    chat_box.config(state=tk.DISABLED)
    chat_box.see(tk.END)
    
def send_file_gui():
    file_path = filedialog.askopenfilename(defaultextension=".txt")
    if file_path:
        send_file(client_socket, file_path)

def send_video_gui():
    file_path = filedialog.askopenfilename(defaultextension=".mp4")
    if file_path:
        send_video(client_socket, file_path)

def close_app():
    try:
        client_socket.close()
    except:
        pass
    window.quit()

def connect_to_server():
    global client_socket, client_name

    ip = ip_entry.get()
    client_name = simpledialog.askstring("Name", "Enter your name:")

    if not client_name:
        return

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, 12345))
        client_socket.send(client_name.encode())
        status_label.config(text=f"Connected as {client_name}", fg="green")
        send_btn.config(state=tk.NORMAL)
        file_btn.config(state=tk.NORMAL)
        video_btn.config(state=tk.NORMAL)
        threading.Thread(target=receive_messages, daemon=True).start()
    except Exception as e:
        messagebox.showerror("Connection Failed", str(e))

# GUI Setup
window = tk.Tk()
window.title("Chat App")
window.geometry("500x600")

status_label = tk.Label(window, text="Disconnected", fg="red")
status_label.pack()

ip_label = tk.Label(window, text="Server IP:")
ip_label.pack()
ip_entry = tk.Entry(window)
ip_entry.pack()

connect_btn = tk.Button(window, text="Connect", command=connect_to_server)
connect_btn.pack()

chat_box = tk.Text(window, height=15, width=60, state=tk.DISABLED)
chat_box.pack(pady=10)

message_entry = tk.Entry(window, width=50)
message_entry.pack()

send_btn = tk.Button(window, text="Send", command=send_message, state=tk.DISABLED)
send_btn.pack(pady=5)

file_btn = tk.Button(window, text="Send File", command=send_file_gui, state=tk.DISABLED)
file_btn.pack()

video_btn = tk.Button(window, text="Send Video File", command=send_video_gui, state=tk.DISABLED)
video_btn.pack()

exit_btn = tk.Button(window, text="Exit", command=close_app)
exit_btn.pack(pady=10)

window.mainloop()
