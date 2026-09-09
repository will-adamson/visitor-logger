"""
Live camera stream for checking focus in real time.
Run this on the Pi, then open http://<pi-ip-address>:8000 in a browser
on your laptop to see a continuously updating live view.
Press Ctrl+C on the Pi to stop.

BEGIN: adapted from Raspberry Pi's official picamera2 MJPEG streaming example
https://github.com/raspberrypi/picamera2/blob/main/examples/mjpeg_server.py
"""

import io
from http import server
from threading import Condition

from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput

PAGE = """\
<html>
<head><title>Camera Focus Check</title></head>
<body><img src="stream.mjpg" width="640" height="480" /></body>
</html>
"""


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', '0')
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', str(len(frame)))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception:
                pass  # client disconnected - nothing to do
        else:
            self.send_error(404)


class StreamingServer(server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True
# END: adapted from picamera2 mjpeg_server.py example


picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
output = StreamingOutput()
picam2.start_recording(MJPEGEncoder(), FileOutput(output))

try:
    print("Streaming - open http://<pi-ip-address>:8000 in a browser on your laptop")
    server_instance = StreamingServer(('', 8000), StreamingHandler)
    server_instance.serve_forever()
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    picam2.stop_recording()
