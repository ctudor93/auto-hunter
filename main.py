import pyautogui
import pygetwindow as gw
from pywinauto import Desktop
import time
import cv2
import numpy as np
import mss

# Define the screen region to capture
monitor = {"top": 100, "left": 100, "width": 800, "height": 600}


# windows = Desktop(backend="uia").windows()

# print([w.window_text() for w in windows])

# for x in pyautogui.getAllWindows():
#     if "Poke" in x.title:
#         print(x.title + "yyyyyyyyyyyyyyyy")
#     else:
#         print(x.title)
# print( pyautogui.getWindowsWithTitle("PokeMMO")[0].isActive() )
# pyautogui.getWindowsWithTitle("РokeMМO")[0].minimize





#Define the target window name (or a part of its name)
target_window_title = pyautogui.getWindowsWithTitle("mozilla")[0].title  


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

while True:
    # Capture the current frame
    current_frame = screen_capture()
    
    # Detect change between frames
    if detect_change(prev_frame, current_frame):
        print("Change detected!")
        
        # Attempt to bring the target application to focus
        if bring_window_to_front(target_window_title):
            # Simulate an input action
            # pyautogui.write("Hello, world!")  # Example: Typing a string
            pyautogui.press("F5")          # Pressing Enter
            
    # Update previous frame
    prev_frame = current_frame
    
    # Slow down the loop to prevent too frequent captures
    time.sleep(1)