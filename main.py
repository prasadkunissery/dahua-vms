import tkinter as tk
import cv2
from PIL import Image, ImageTk
import threading

class RTSPViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Video Stream")
        
        # Keep window always on top as requested
        self.root.attributes("-topmost", True)
        
        # Handle the close event properly to clean up resources
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Video frame dimensions for the small popup (480x320)
        self.video_width = 480
        self.video_height = 320

        # Create a placeholder black image for the video area
        self.placeholder = Image.new('RGB', (self.video_width, self.video_height), color='black')
        self.placeholder_tk = ImageTk.PhotoImage(self.placeholder)

        # --- UI Elements Layout ---
        
        # 1. Live Video Area
        self.video_label = tk.Label(root, image=self.placeholder_tk)
        self.video_label.pack(pady=5, padx=5)

        # 2. Status Label
        self.status_label = tk.Label(root, text="Disconnected", fg="red", font=("Arial", 10, "bold"))
        self.status_label.pack(pady=2)

        # 3. Control Buttons Area
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        self.connect_btn = tk.Button(button_frame, text="Connect", width=10, command=self.connect_stream)
        self.connect_btn.pack(side=tk.LEFT, padx=5)

        self.disconnect_btn = tk.Button(button_frame, text="Disconnect", width=10, command=self.disconnect_stream, state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT, padx=5)

        self.close_btn = tk.Button(button_frame, text="Close", width=10, command=self.on_closing)
        self.close_btn.pack(side=tk.LEFT, padx=5)

        # --- Stream Management Variables ---
        self.cap = None
        self.is_running = False
        self.thread = None

        # --- IMPORTANT SECURITY NOTE ---
        # WARNING: In a production environment, avoid hardcoding sensitive credentials.
        # Consider using environment variables, OS keychains, or secure configuration files.
        username = "admin"
        password = "admin123"
        base_address = "61.13.222.78:8080/cam/realmonitor?channel=1&subtype=0"
        
        # Construct RTSP URL with inline authentication
        self.rtsp_url = f"rtsp://{username}:{password}@{base_address}"

    def connect_stream(self):
        """Triggered by the Connect button to start the video stream processing."""
        if not self.is_running:
            self.status_label.config(text="Connecting...", fg="orange")
            self.connect_btn.config(state=tk.DISABLED)
            
            # Start background thread to avoid freezing the UI during connection and reading
            self.is_running = True
            self.thread = threading.Thread(target=self.video_loop, daemon=True)
            self.thread.start()

    def process_frame(self, frame):
        """Runs in the main thread to update the Tkinter canvas safely."""
        # 1. Resize frame to fit the 480x320 popup window
        frame_resized = cv2.resize(frame, (self.video_width, self.video_height))
        # 2. Convert Color Space BGR -> RGB for PIL compatibility
        cv2image = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        # 3. Create Pillow Image
        img = Image.fromarray(cv2image)
        # 4. Create Tkinter PhotoImage and update Label
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk # Keep strong reference to avoid garbage collection
        self.video_label.config(image=imgtk)

    def video_loop(self):
        """Runs in a background thread to capture video frames sequentially."""
        # Attempt to establish connection to the RTSP source
        # Note: Depending on the network, cv2.VideoCapture block can take a few seconds
        self.cap = cv2.VideoCapture(self.rtsp_url)
        
        if not self.cap.isOpened():
            # Handle connection failure gracefully
            self.is_running = False
            self.root.after(0, self.update_status, "Connection failed", "red")
            self.root.after(0, self.reset_buttons)
            return

        # Successfully connected
        self.root.after(0, self.update_status, "Connected", "green")
        self.root.after(0, lambda: self.disconnect_btn.config(state=tk.NORMAL))

        while self.is_running:
            ret, frame = self.cap.read()
            if ret:
                # Schedule frame processing on the main Tkinter UI thread
                self.root.after(0, self.process_frame, frame)
            else:
                # Stream ends or is dropped
                self.is_running = False
                self.root.after(0, self.update_status, "Connection lost", "red")
                self.root.after(0, self.clear_video)
                self.root.after(0, self.reset_buttons)
                break
                
        # Clean up camera feed
        if self.cap:
            self.cap.release()

    def disconnect_stream(self):
        """Triggered by the Disconnect button to manually stop the stream."""
        self.is_running = False
        self.update_status("Disconnected", "red")
        self.clear_video()
        self.reset_buttons()

    def update_status(self, text, color):
        """Thread-safe status update wrapper."""
        self.status_label.config(text=text, fg=color)

    def reset_buttons(self):
        """Reverts the buttons back to the default disconnected state."""
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)

    def clear_video(self):
        """Resets the video area to the default black placeholder."""
        self.video_label.config(image=self.placeholder_tk)
        self.video_label.imgtk = self.placeholder_tk

    def on_closing(self):
        """Ensures that the thread and OpenCV object release cleanly when window closes."""
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RTSPViewer(root)
    # Start the Tkinter event loop
    root.mainloop()
