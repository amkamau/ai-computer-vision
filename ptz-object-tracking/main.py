import cv2
import torch
import time
from ultralytics import YOLO

# Load a model
model = YOLO("../Yolov26/models/detection/yolo26m.pt")  # load an official model
# model = YOLO("../Yolov26/models/pose/yolo26m-pose.pt")  # load an official model
# model = YOLO("../Yolov26/models/segment/yolo26m-seg.pt")  # load an official model
# model = YOLO("../Yolov26/models/classify/yolo26m-cls.pt")  # load an official model
# model = YOLO("../Yolov26/models/obb/yolo26m-obb.pt")  # load an official model
# model = YOLO("../Yolov26/models/sematic/yolo26l-sem.pt")  # load an official model

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
print("Using:", device)

# Load videos source
vid_src = ["rtsp://admin:Qwerty@321@192.168.0.80:554/Streaming/Channels/101/","../sample.mp4"]

def main(args):

    cap = cv2.VideoCapture(vid_src[1]) #IP Camera
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("Video FPS:", fps)
    prev_time = time.time()

    while(True):
        ret, frame = cap.read()

        if not ret: break

        frame = cv2.resize(frame, (1280, 720))
        results = model(frame, imgsz=640, device=0, verbose=False)

        frame  = results[0].plot()

        fps = 1 / (time.time() - prev_time)
        prev_time = time.time()

        cv2.putText(frame, f"FPS: {fps:.1f}",(20, 40),cv2.FONT_HERSHEY_SIMPLEX, 1,(0, 255, 0),2)
        cv2.imshow("Detection", frame)



        
        if cv2.waitKey(1) & 0xFF == ord('q'): break  #click q to stop capturing


    cap.release()
    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))


