from ultralytics import YOLO
import cv2
import numpy as np
from tqdm import tqdm

VEHICLE_CLASSES = {2, 3, 5, 7}

def _find_plate_boxes(veh_roi):
    if veh_roi.size == 0:
        return []
    h0, w0 = veh_roi.shape[:2]
    scale = 640.0 / max(w0, 1)
    proc = cv2.resize(veh_roi, (max(1, int(w0*scale)), max(1, int(h0*scale))))
    ph, pw = proc.shape[:2]
    gray = cv2.cvtColor(proc, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 7, 50, 50)
    gradx = cv2.Sobel(gray, cv2.CV_16S, 1, 0, ksize=3)
    gradx = cv2.convertScaleAbs(gradx)
    gradx = cv2.normalize(gradx, None, 0, 255, cv2.NORM_MINMAX)
    _, th = cv2.threshold(gradx, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    closed = cv2.morphologyEx(th, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT,(17,3)), iterations=2)
    closed = cv2.morphologyEx(closed, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT,(3,3)), iterations=1)
    y_focus = int(ph*0.4)
    mask = np.zeros_like(closed); mask[y_focus:ph,:]=255
    foc = cv2.bitwise_and(closed, mask)
    contours,_ = cv2.findContours(foc, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []
    for c in contours:
        x,y,w,h = cv2.boundingRect(c)
        if w<30 or h<12: continue
        aspect = w/float(h); area = w*h
        rect_area = cv2.contourArea(c)
        fill = rect_area/float(area+1e-6)
        if 1.8<=aspect<=6.5 and 0.45<=fill<=1.0:
            roi = gradx[y:y+h, x:x+w]
            edge = float(cv2.countNonZero(roi))/(w*h)
            if edge < 0.10: continue
            pad_x=int(w*0.06); pad_y=int(h*0.25)
            x1=max(0,x-pad_x); y1=max(0,y-pad_y)
            x2=min(pw,x+w+pad_x); y2=min(ph,y+h+pad_y)
            candidates.append((x1,y1,x2,y2, area, aspect, edge))
    candidates.sort(key=lambda t:(t[4]*(t[6]+0.5)), reverse=True)
    top = candidates[:2]
    inv = 1.0/max(scale,1e-6)
    boxes=[]
    for (x1,y1,x2,y2, *_ ) in top:
        X1=int(x1*inv); Y1=int(y1*inv); X2=int(x2*inv); Y2=int(y2*inv)
        X1=max(0,min(X1,w0-1)); X2=max(0,min(X2,w0)); Y1=max(0,min(Y1,h0-1)); Y2=max(0,min(Y2,h0))
        if X2>X1 and Y2>Y1: boxes.append((X1,Y1,X2,Y2))
    return boxes

def blur_plates_video(input_video, output_video, yolo_path="yolov8s.pt", k=51, conf=0.25, iou=0.45):
    model = YOLO(yolo_path)
    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {input_video}")
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_video, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W,H))
    logs = [f"[INFO] Blurring {input_video} → {output_video}"]
    with tqdm(total=total, desc="Blurring Plates", unit="frame") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret: break
            det_w = 1280; det_h = int(H*det_w/max(W,1))
            det = cv2.resize(frame, (det_w, det_h))
            results = model(det, conf=conf, iou=iou, verbose=False)
            for r in results:
                for box, cls in zip(r.boxes.xyxy, r.boxes.cls):
                    if int(cls) not in {2,3,5,7}: continue
                    x1d,y1d,x2d,y2d = map(int, box)
                    sx = W/det_w; sy = H/det_h
                    x1=max(0,int(x1d*sx)); y1=max(0,int(y1d*sy))
                    x2=min(W,int(x2d*sx)); y2=min(H,int(y2d*sy))
                    xpad=int((x2-x1)*0.03); ypad=int((y2-y1)*0.03)
                    x1=max(0,x1+xpad); y1=max(0,y1+ypad); x2=min(W,x2-xpad); y2=min(H,y2-ypad)
                    veh_roi = frame[y1:y2, x1:x2]
                    for (px1,py1,px2,py2) in _find_plate_boxes(veh_roi):
                        X1=x1+px1; Y1=y1+py1; X2=x1+px2; Y2=y1+py2
                        roi = frame[Y1:Y2, X1:X2]
                        if roi.size==0: continue
                        kk = k if (k%2==1) else (k+1)
                        frame[Y1:Y2, X1:X2] = cv2.GaussianBlur(roi, (kk,kk), 0)
            out.write(frame); pbar.update(1)
    cap.release(); out.release()
    logs.append("[INFO] Done.")
    return logs
