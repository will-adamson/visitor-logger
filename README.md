# visitor-logger

A visitor logging system that combines an Arduino sensor with a Raspberry Pi. When someone walks up to the ultrasonic sensor, the Pi takes a photo. If a face is detected, the visit is saved to a SQLite database. Visits and statistics are shown on a live web dashboard that any device on the same network can view.

## Software setup

### Arduino

Upload `SensorPySerial/SensorPySerial.ino` to the Arduino.

### Raspberry Pi

You don't have to run a headless distro of the Raspberry Pi distro, but that's what I used.

```bash
sudo apt update
sudo apt install python3-picamera2 python3-serial python3-flask
pip install opencv-python --break-system-packages
git clone https://github.com/will-adamson/visitor-logger.git
cd visitor-logger
```

### Network

Connect to wifi:
```bash
sudo nmcli device wifi connect "<network name>" password "<password>"
```

## Running it

### 1. Focus the camera

```bash
hostname -I   # shows the Pi's IP address
python3 live_focus_check.py
```
Open `http://<pi-ip>:8000` in a browser on the same network, and twist the lens until a face at the expected distance is sharp. Press Ctrl+C to stop. The camera can only be used by one program at a time, so this must be stopped before starting `main.py`.

### 2. Start the logger and dashboard

```bash
python3 main.py &
python3 dashboard.py
```
It will start printing the detection range to command line once it's working.

Open `http://<pi-ip>:5000` on any device on the same network.

### 3. Calibrate the detection range

Turn the potentiometer to set how close someone needs to be to trigger a photo (20 to 100 cm). The current range is shown on the dashboard. If the range reaches a wall or other object behind the sensor, nothing new will trigger, so turn it down until it stops short of the background.

### 4. Shutdown

Ctrl + C to close the dashboard, then type
```bash
fg
```
to bring the main.py program to the foreground, then Ctrl + C again to close it.

## Failsafes

- **Watchdog timer:** if the Arduino's code freezes for 2 seconds, the hardware watchdog resets it automatically.
- **Heartbeat timeout:** if the Pi receives nothing from the Arduino for 5 seconds, `main.py` stops with a clear error instead of waiting forever.
- **Detection cooldown:** after a visitor is detected, new triggers are ignored for 3 seconds, so one visit gives one photo.