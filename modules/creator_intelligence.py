import json, numpy as np
from pathlib import Path

def _audio_energy(wav_path: str):
    try:
        import librosa
        y, sr = librosa.load(wav_path, sr=None, mono=True)
        rmse = librosa.feature.rms(y=y, frame_length=2048, hop_length=512).flatten()
        rmse = (rmse - rmse.min()) / (rmse.max()-rmse.min()+1e-9)
        return rmse, len(rmse), 512/float(sr)
    except Exception:
        return np.array([0.5]), 1, 1.0

def _motion_score(video_path: str, step=10):
    try:
        import cv2
        cap = cv2.VideoCapture(video_path); prev=None; scores=[]; i=0
        while True:
            ret, frame = cap.read()
            if not ret: break
            if i % step != 0: i+=1; continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if prev is not None:
                diff = cv2.absdiff(gray, prev); scores.append(float(diff.mean())/255.0)
            prev = gray; i+=1
        cap.release()
        if not scores: return [0.5]
        s = np.array(scores); s = (s - s.min())/(s.max()-s.min()+1e-9)
        return s.tolist()
    except Exception:
        return [0.5]

def compute_virality_score(video_path: str, transcript_json: str, audio_wav: str, target_len=30.0):
    # audio energy + motion windowing
    rmse, n, hop_sec = _audio_energy(audio_wav)
    motion = np.array(_motion_score(video_path))
    L = max(len(rmse), len(motion))
    rmse = np.interp(np.linspace(0, len(rmse)-1, L), np.arange(len(rmse)), rmse) if len(rmse)>1 else np.full(L, rmse[0])
    motion = np.interp(np.linspace(0, len(motion)-1, L), np.arange(len(motion)), motion) if len(motion)>1 else np.full(L, motion[0])
    score = 0.6*rmse + 0.4*motion
    win = max(1, int(target_len / max(hop_sec,1e-3)))
    best_i, best_v = 0, -1
    cumsum = np.cumsum(np.concatenate([[0], score]))
    for i in range(0, len(score)-win):
        v = cumsum[i+win]-cumsum[i]
        if v > best_v: best_v, best_i = v, i
    start = float(best_i*hop_sec); end = start + float(target_len)
    return [{"start": max(0.0, start), "end": max(start+0.3, end), "score": float(best_v)/max(win,1), "mood":"energetic"}]
