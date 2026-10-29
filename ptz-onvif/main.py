import cv2
import time
import mouse_ptz_class
from camera_onvif_class import PTZCamera


# Load videos source
camera_src = "rtsp://guest:Guest123@192.168.0.200:554/Streaming/Channels/101/"

inverted = True

mouse_x = 0
mouse_y = 0

def mouse_callback(event, x, y, flags, param):
    global mouse_x, mouse_y
    if event == cv2.EVENT_MOUSEMOVE:
        mouse_x = x
        mouse_y = y

cv2.namedWindow("Camera")
cv2.setMouseCallback("Camera", mouse_callback)

camera = PTZCamera(host="192.168.0.200", port=80, username="admin", password="Qwerty@321")
controller = mouse_ptz_class.MousePTZController(camera)


def main(args):

    cap = cv2.VideoCapture(camera_src) #IP Camera
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("Video FPS:", fps)
    prev_time = time.time()



    while(True):

        ret, frame = cap.read()

        if not ret: 
            break

        if inverted: 
            frame = cv2.rotate(frame, cv2.ROTATE_180)
        frame = cv2.resize(frame, (1280, 720))

        fps = 1 / (time.time() - prev_time)
        prev_time = time.time()

        cv2.putText(frame, f"FPS: {fps:.1f}",(20, 40),cv2.FONT_HERSHEY_SIMPLEX, 1,(0, 255, 0),2)
        cv2.imshow("Camera", frame)

        controller.update( mouse_x, mouse_y,frame.shape[1],frame.shape[0])

        if cv2.waitKey(1) & 0xFF == ord('q'): break  #click q to stop capturing

    cap.release()
    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))


