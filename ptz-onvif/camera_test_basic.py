from camera_onvif_class import PTZCamera
import time


camera = PTZCamera(host="192.168.0.200", port=80, username="guest", password="Guest123")

camera.pan_right(1.0)
camera.tilt_down(1.0)
camera.zoom_in()

time.sleep(1)

camera.stop()
camera.zoom_out()