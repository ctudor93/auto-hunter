import pyautogui
import pygetwindow as gw
from pywinauto import Desktop
import time
import cv2
import numpy as np
import mss
import tkinter as tk
from tkinter import messagebox
import threading 
import pytesseract
from PIL import ImageGrab, Image, ImageTk  

# Define the screen region to capture
monitor = {"top": 100, "left": 100, "width": 800, "height": 600}

#bool used to stop the program from running
stop = False

# Variable to store thread
main_thread = None 

changes_counter=0

#Define the target window name (or a part of its name)
target_window_title = pyautogui.getWindowsWithTitle("mozilla")[0].title  

# Ensure pytesseract can be found in the path
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"  # Adjust if necessary


# windows = Desktop(backend="uia").windows()

# print([w.window_text() for w in windows])

# for x in pyautogui.getAllWindows():
#     if "Poke" in x.title:
#         print(x.title + "yyyyyyyyyyyyyyyy")
#     else:
#         print(x.title)
# print( pyautogui.getWindowsWithTitle("PokeMMO")[0].isActive() )
# pyautogui.getWindowsWithTitle("РokeMМO")[0].minimize


# Global variables to store the selection rectangle
x_start, y_start, x_end, y_end = 0, 0, 0, 0
selecting = False

def select_area(event):
    global x_start, y_start, x_end, y_end, selecting
    selecting = True
    x_start, y_start = event.x, event.y

def release_area(event):
    global selecting, x_end, y_end
    selecting = False
    x_end, y_end = event.x, event.y
    canvas.create_rectangle(x_start, y_start, x_end, y_end, outline="red", width=2)

def capture_and_process():
    if x_start == x_end or y_start == y_end:
        messagebox.showwarning("Invalid Selection", "Please select a valid area!")
        return
    
    # Capture the screen region as a numpy array
    bbox = (x_start, y_start, x_end, y_end)
    screenshot = ImageGrab.grab(bbox)

    # Convert to OpenCV format
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Use pytesseract to perform OCR
    extracted_text = pytesseract.image_to_string(img)
    
    # Display extracted text in a messagebox
    messagebox.showinfo("Extracted Text", extracted_text)

def run_capture_screen():
    # Capture the entire screen and display it in a canvas for selection
    screen = np.array(ImageGrab.grab(bbox=None))  # Full screen capture
    screen_bgr = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
    
    # Convert screen_bgr (OpenCV) to Image format for Tkinter display
    image_pil = Image.fromarray(screen_bgr)  # Convert to PIL Image

    # Create a PhotoImage for the canvas using ImageTk
    screen_img = ImageTk.PhotoImage(image=image_pil)
    canvas.create_image(0, 0, anchor=tk.NW, image=screen_img)
    canvas.image = screen_img  # Keep a reference to prevent garbage collection


def bring_window_to_front(window_title):
    try:
        # Get the window by title
        target_window = gw.getWindowsWithTitle(window_title)[0]
        target_window.activate()  # Bring the window to the front and give it focus
        print(f"Brought {window_title} to focus.")
        return True
    except IndexError:
        print(f"Window with title '{window_title}' not found.")
        return False

def screen_capture():
    with mss.mss() as sct:
        img = np.array(sct.grab(monitor))
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

def detect_change(img1, img2, threshold=5):
    diff = cv2.absdiff(img1, img2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return cv2.countNonZero(thresh) > 0


# Initial screen capture
prev_frame = screen_capture()

def main():
    global stop, prev_frame
    while not stop:
        
        # Capture the current frame
        current_frame = screen_capture()
        
        # Detect change between frames
        if detect_change(prev_frame, current_frame):
            print("Change detected!")
            
            # Attempt to bring the target application to focus
            if bring_window_to_front(target_window_title):
                # Simulate an input action
                # pyautogui.write("Hello, world!")  # Example: Typing a string
                # pyautogui.press("F5")          # Pressing Enter
                global changes_counter 
                changes_counter+=1
                print(changes_counter)
                
        # Update previous frame
        prev_frame = current_frame
        
        # Slow down the loop to prevent too frequent captures
        time.sleep(1)
    
def start_program():
    global main_thread, stop
    stop = False # Reset stop flag
    
    #Run main() in a separate thread
    main_thread = threading.Thread(target= main)
    main_thread.start()
    start_button.config( state= tk.DISABLED ) #Disable start button to prevent rerunning
    

def stop_program():
    global stop 
    stop = True
    stop_button.config(text=str(stop) )
    print("Programmed stopped ")
    start_button.config(state=tk.ACTIVE) #Enable start button after stopping 

def close_window():
    global app
    stop_program()
    app.destroy()


# Create the main application window
app = tk.Tk()
app.title("test")

# Create and configure canvas for screen capture
canvas = tk.Canvas(app, width=400, height=400, bg="red")
canvas.pack()

# Bind mouse events for selecting rectangle
canvas.bind("<ButtonPress-1>", select_area) # Mouse button 1 press
canvas.bind("<ButtonRelease-1>", release_area) # Mouse button 1 release

# Create buttons for screen capture and selection processing
capture_button = tk.Button(app, text="Capture screen", command=run_capture_screen)
capture_button.pack(pady=10)

process_button = tk.Button(app, text="Process capture", command=capture_and_process)
process_button.pack(pady=10)


# Create buttons for starting, stopping and quitting app
start_button = tk.Button(app, text="Start", command=start_program)
start_button.pack()

stop_button = tk.Button(app, text = str(stop), command=stop_program)
stop_button.pack()

close_button = tk.Button(app, text="Exit", command=close_window)
close_button.pack(side="bottom")

# Start the Tkinter event loop
app.minsize(400,800)
app.mainloop()