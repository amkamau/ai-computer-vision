import cv2

src_channel = 1

def init_cap(src_channel):
    url = "rtsp://username:password@192.168.x.x:554/H264/ch" + str(src_channel)
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        exit()
    return cap



cap = init_cap(src_channel)

while True:

    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (1280, 720))


    cv2.putText(frame, f"Channel {src_channel}", (20, 40),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("RTSP Camera", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    if key == ord("c"):
       src_channel = 2 if src_channel == 1 else 1
       cap.release()
       cap = init_cap(src_channel)


cap.release()
cv2.destroyAllWindows()
