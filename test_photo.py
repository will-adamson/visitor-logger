"""
Quick focus-testing script.
Press Enter to take a photo, saved into images/ with a timestamped filename.
Type 'q' then Enter to quit.
"""

import os
from datetime import datetime
from picamera2 import Picamera2

picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

os.makedirs("images", exist_ok=True)

print("Press Enter to take a photo, or 'q' + Enter to quit.")

while True:
    user_input = input("> ")
    if user_input.strip().lower() == "q":
        break

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    photo_path = f"images/{timestamp}.jpg"
    picam2.capture_file(photo_path)
    print(f"Saved {photo_path}")

picam2.stop()
print("Done.")
