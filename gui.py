import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
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
            log_chat(f"{client_name} (You): {message}")
            message_entry.delete(0, tk.END)
        except:
            messagebox.showerror("Error", "Failed to send message.")

def receive_messages():
    while True:
        try:
            msg = client_socket.recv(14)
            if not msg:
                break

            decoded = msg.decode('utf-8', errors='ignore')
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
                message = client_socket.recv(1024).decode(errors='ignore')
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
        status_label.config(text=f"Connected as {client_name}", foreground="green")
        send_btn.config(state=tk.NORMAL)
        file_btn.config(state=tk.NORMAL)
        video_btn.config(state=tk.NORMAL)
        threading.Thread(target=receive_messages, daemon=True).start()
    except Exception as e:
        messagebox.showerror("Connection Failed", str(e))

# GUI Setup
window = tk.Tk()
window.title("Private Chat Room")
window.geometry("580x650")
window.configure(bg="#e6f0f7")

header = tk.Label(window, text="🔒 Welcome to the Secure Chat Room", font=("Helvetica", 16, "bold"), bg="#e6f0f7", fg="#003366")
header.pack(pady=(10, 5))

status_label = tk.Label(window, text="Disconnected", fg="red", bg="#e6f0f7", font=("Helvetica", 10, "italic"))
status_label.pack()

connection_frame = tk.Frame(window, bg="#e6f0f7")
connection_frame.pack(pady=10)

ip_label = tk.Label(connection_frame, text="Server IP:", bg="#e6f0f7", font=("Helvetica", 11))
ip_label.grid(row=0, column=0, padx=5)

ip_entry = tk.Entry(connection_frame, width=30)
ip_entry.grid(row=0, column=1, padx=5)

connect_btn = tk.Button(connection_frame, text="Connect", bg="#4CAF50", fg="white", command=connect_to_server)
connect_btn.grid(row=0, column=2, padx=5)

chat_box = tk.Text(window, height=20, width=70, bg="white", font=("Helvetica", 10), wrap="word", relief="solid", bd=1)
chat_box.pack(pady=10)
chat_box.config(state=tk.DISABLED)

message_frame = tk.Frame(window, bg="#e6f0f7")
message_frame.pack(pady=5)

message_entry = tk.Entry(message_frame, width=45)
message_entry.grid(row=0, column=0, padx=5)

send_btn = tk.Button(message_frame, text="Send", bg="#2196F3", fg="white", command=send_message, state=tk.DISABLED)
send_btn.grid(row=0, column=1, padx=5)

file_btn = tk.Button(window, text="📄 Send File", width=20, bg="#f0ad4e", fg="white", command=send_file_gui, state=tk.DISABLED)
file_btn.pack(pady=4)

video_btn = tk.Button(window, text="🎥 Send Video", width=20, bg="#5bc0de", fg="white", command=send_video_gui, state=tk.DISABLED)
video_btn.pack(pady=4)

exit_btn = tk.Button(window, text="🚪 Exit", width=20, bg="#d9534f", fg="white", command=close_app)
exit_btn.pack(pady=15)

window.mainloop()