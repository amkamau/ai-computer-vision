import cv2
import torch
import time
from ultralytics import YOLO
import numpy as np

# Load a model
model = YOLO("../.models/yolov26/detection/yolo26n.pt")
""
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
print("Using:", device)

# Load videos source
vid_src = ["rtsp://guest:Guest123@192.168.0.80:554/Streaming/Channels/101/","../media/sample1.mp4"]

is_tracking = True
is_plot = True

selected_id = {}
current_tracks = ()

unique_track_ids = set()
track_start_times = {}



def mouse_callback(event, x, y, flags, param):
    global selected_id
    if event == cv2.EVENT_LBUTTONDOWN:
        if current_tracks is None:
            return
        boxes, track_ids, classes, confidences = current_tracks
        for box, track_id, cls, conf in zip(boxes, track_ids, classes, confidences):
            x1, y1, x2, y2 = map(int, box)
            if x1 <= x <= x2 and y1 <= y <= y2:
                if selected_id == track_id:
                    selected_id = None  # Toggle selection off
                else:
                    selected_id = track_id
                return
            


def update_current_tracks(result):
    global current_tracks    
    if result.boxes.id is None:
        current_tracks = None
        return
    boxes = result.boxes.xyxy.cpu().numpy()
    track_ids = result.boxes.id.int().cpu().numpy()
    classes = result.boxes.cls.int().cpu().numpy()
    confidences = result.boxes.conf.cpu().numpy()
    current_tracks = (boxes, track_ids, classes, confidences)



def draw_selected_object(frame):
    if current_tracks is None or selected_id is None:
        return

    boxes, track_ids, classes, confidences = current_tracks

    for box, track_id, cls, conf in zip(boxes, track_ids, classes, confidences):
        if track_id == selected_id:
            x1, y1, x2, y2 = map(int, box)
            # Highlight bounding box in red, with a thicker border
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4)
            # Display selected object information
            label = f"SELECTED ID:{track_id} | {model.names[int(cls)]}"
            (text_w, text_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(frame, (x1, max(0, y1 - text_h - baseline - 8)), (x1 + text_w + 8, y1), (0, 0, 255), -1)
            cv2.putText(frame, label, (x1 + 4, y1 - baseline - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

            break



def join_frame(frame, fps, inference_ms):
    height, width = frame.shape[:2]
    panel = np.zeros((170, width, 3), dtype=np.uint8)

    tracks = current_tracks
    boxes, ids, classes, confs = tracks if tracks is not None else ([], [], [], [])

    # Detection counts by class
    counts = {}
    for cls in classes:
        name = model.names[int(cls)]
        counts[name] = counts.get(name, 0) + 1

    class_text = "  ".join(f"{k}: {v}" for k, v in counts.items()) or "None"
    avg_conf = float(np.mean(confs)) if len(confs) else 0.0

    # Selected object details
    selected = next((i for i, tid in enumerate(ids) if int(tid) == selected_id), None)
    if selected is not None:
        x1, y1, x2, y2 = map(int, boxes[selected])
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        size = f"{x2-x1}x{y2-y1}"
        name = model.names[int(classes[selected])]
        conf = confs[selected]
        duration = time.time() - track_start_times.get(selected_id, time.time())
        selected_text = f"ID: {selected_id} | {name} | Conf: {conf:.2f} ---- [ Center: ({cx}, {cy}) | Size: {size}px | Duration: {duration:.1f}s ]"
    else:
        selected_text = f"ID: {selected_id} | Not visible" if selected_id is not None else "No object selected"


    cv2.putText(panel, f"FPS : {fps:.1f}", (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 255, 100), 1, cv2.LINE_AA)
    cv2.putText(panel, f"*  Inference : {inference_ms:.1f} ms", (150, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.putText(panel, f"*  Detections : {len(ids)}", (350, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.putText(panel, f"*  Unique tracks : {len(unique_track_ids)}", (550, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.putText(panel, f"*  Avg confidence : {avg_conf:.2f}", (750, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.putText(panel, f"**  {selected_text}", (25, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 200), 1, cv2.LINE_AA)
    cv2.putText(panel, f"**  Classes : {class_text}", (25, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)

    return np.vstack((frame, panel))




def main(args):

    cap = cv2.VideoCapture(vid_src[1])
    source_fps = cap.get(cv2.CAP_PROP_FPS)
    print(source_fps)
    prev_time = time.time()


    window_name = "ObjectTracker"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, mouse_callback)
    # cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while(True):

        ret, frame = cap.read()        

        if not ret: 
            break

        frame = cv2.resize(frame, (1280, 720))

        start = time.perf_counter()        
        results = model.track(frame, tracker="botsort.yaml", persist=True,verbose=False)
        inference_ms = (time.perf_counter() - start) * 1000

        update_current_tracks(results[0])
        if current_tracks is not None:
            for track_id in current_tracks[1]:
                track_id = int(track_id)
                unique_track_ids.add(track_id)
                track_start_times.setdefault(track_id, time.time())
        
        frame = results[0].plot(line_width=2)

        draw_selected_object(frame)

        fps = 1 / max(time.perf_counter() - prev_time, 1e-9)
        prev_time = time.perf_counter()

        frame = join_frame(frame, fps, inference_ms)
        cv2.imshow(window_name, frame)
        print(fps)

        if cv2.waitKey(1) & 0xFF == ord('q'): break  #click q to stop capturing

    cap.release()
    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))


