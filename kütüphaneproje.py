import cv2
import psutil
import time
import requests
import threading
import os
import numpy as np
import tkinter as tk
import keyboard
import pyttsx3
import io
import sounddevice as sd
from scipy.io.wavfile import write
from tkinter import scrolledtext
from datetime import datetime
from flask import Flask, Response

# --- AYARLAR ---
TELEGRAM_TOKEN = ""
CHAT_ID = ""
COOLDOWN = 10

app_web = Flask(__name__)
global_frame = None


class SiberMuhafizV18:
    def __init__(self, root):
        self.root = root
        self.root.title("SİBER MUHAFIZ v18.1")
        self.root.geometry("500x800")
        self.root.configure(bg="#000000")

        self.is_running = False
        self.last_update_id = 0
        self.is_visible = True
        self.is_locked = False  # Kilitleme durumu kontrolü

        # Biometrik Değişkenler
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.is_trained = False
        self.is_recording_video = False

        # Ses Kayıt Değişkenleri
        self.is_recording_audio = False
        self.audio_data = []
        self.fs = 44100

        self.setup_ui()
        threading.Thread(target=lambda: app_web.run(host='0.0.0.0', port=5000), daemon=True).start()
        threading.Thread(target=self.listen_hotkeys, daemon=True).start()

    def setup_ui(self):
        tk.Label(self.root, text="--- SIBER GUARD V18.1 ---", fg="#00ff00", bg="#000000", font=("Courier", 12)).pack(
            pady=10)
        self.status_label = tk.Label(self.root, text="STATUS: IDLE", fg="#ff0000", bg="#000000",
                                     font=("Courier", 14, "bold"))
        self.status_label.pack(pady=5)

        # Hata Çözümü: fg (renk) parametresini stilden çıkarıp butonlara özel verdik
        base_btn_style = {"bg": "#000000", "font": ("Courier", 10), "borderwidth": 2, "relief": "flat"}

        tk.Button(self.root, text="[ BIOMETRIC SCAN ]", command=self.train_face, fg="#00ff00", **base_btn_style, width=35).pack(pady=5)
        tk.Button(self.root, text="[ START PROTOCOL ]", command=self.start_system, fg="#00ff00", **base_btn_style, width=35).pack(pady=5)

        # YENI BUTON: LOCKDOWN (Artık çakışma yaşanmaz)
        self.btn_lock = tk.Button(self.root, text="[ ACTIVATE LOCKDOWN ]", command=self.activate_lockdown,
                                  fg="#ff0000", **base_btn_style, width=35)
        self.btn_lock.pack(pady=5)

        self.log_area = scrolledtext.ScrolledText(self.root, width=60, height=25, bg="#000000", fg="#00ff00",
                                                  font=("Courier", 8))
        self.log_area.pack(pady=15, padx=15)

    def add_log(self, msg):
        now = datetime.now().strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"ROOT@SYSTEM:~$ {msg} [{now}]\n")
        self.log_area.see(tk.END)

    def activate_lockdown(self):
        self.is_locked = True
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.config(cursor="none")
        self.add_log("FULL LOCKDOWN ACTIVATED.")
        self.send_telegram_msg("🔐 SİSTEM KİLİTLENDİ. Çözmek için Ctrl+Alt+Q kullanın.")

    def release_lockdown(self):
        self.is_locked = False
        self.root.attributes("-fullscreen", False)
        self.root.attributes("-topmost", False)
        self.root.config(cursor="")
        self.add_log("LOCKDOWN RELEASED.")
        self.send_telegram_msg("🔓 SİSTEM KİLİDİ AÇILDI.")

    def toggle_visibility(self):
        if self.is_visible:
            self.root.withdraw()
            self.is_visible = False
        else:
            self.root.deiconify()
            self.is_visible = True

    def train_face(self):
        self.add_log("SCANNING BIOMETRICS...")
        cap = cv2.VideoCapture(0)
        faces_data, labels, count = [], [], 0
        while count < 30:
            ret, frame = cap.read()
            if not ret: break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                count += 1
                faces_data.append(gray[y:y + h, x:x + w])
                labels.append(1)
            cv2.imshow("SCANNING", frame)
            cv2.waitKey(1)
        cap.release()
        cv2.destroyAllWindows()
        if faces_data:
            self.recognizer.train(faces_data, np.array(labels))
            self.is_trained = True
            self.add_log("BIOMETRICS READY.")

    def record_video_evidence(self, frame_size):
        if self.is_recording_video: return
        self.is_recording_video = True
        filename = f"evid_{int(time.time())}.avi"
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(filename, fourcc, 20.0, (frame_size[1], frame_size[0]))
        start_time = time.time()
        while time.time() - start_time < 6:
            if global_frame is not None: out.write(global_frame)
            time.sleep(0.05)
        out.release()
        try:
            with open(filename, 'rb') as v:
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo",
                              data={'chat_id': CHAT_ID, 'caption': "🚨 BREACH!"}, files={'video': v})
            os.remove(filename)
        except:
            pass
        self.is_recording_video = False

    def monitor_security(self):
        global global_frame
        cap = cv2.VideoCapture(0)
        ret, frame1 = cap.read()
        last_vid_time = 0
        while self.is_running:
            ret, frame2 = cap.read()
            if not ret: continue
            global_frame = frame2.copy()
            diff = cv2.absdiff(frame1, frame2)
            if np.mean(diff) > 25:
                is_intruder = True
                if self.is_trained:
                    gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                    for (x, y, w, h) in faces:
                        _, conf = self.recognizer.predict(gray[y:y + h, x:x + w])
                        if conf < 75: is_intruder = False; break
                if is_intruder and (time.time() - last_vid_time > COOLDOWN):
                    threading.Thread(target=self.record_video_evidence, args=(frame2.shape,)).start()
                    last_vid_time = time.time()
            frame1 = frame2
            time.sleep(0.05)
        cap.release()

    def send_telegram_msg(self, text):
        try:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                          data={'chat_id': CHAT_ID, 'text': text})
        except:
            pass

    def audio_callback(self, indata, frames, time_info, status):
        if self.is_recording_audio: self.audio_data.append(indata.copy())

    def start_audio_record(self):
        if self.is_recording_audio: return
        self.is_recording_audio = True
        self.audio_data = []
        with sd.InputStream(samplerate=self.fs, channels=2, callback=self.audio_callback):
            while self.is_recording_audio: sd.sleep(100)

    def stop_audio_record(self):
        if not self.is_recording_audio: return
        self.is_recording_audio = False
        if self.audio_data:
            filename = f"aud_{int(time.time())}.wav"
            recording = np.concatenate(self.audio_data, axis=0)
            write(filename, self.fs, recording)
            with open(filename, 'rb') as f:
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument", data={'chat_id': CHAT_ID},
                              files={'document': f})
            os.remove(filename)

    def listen_telegram_commands(self):
        while self.is_running:
            try:
                r = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates",
                                 params={'offset': self.last_update_id + 1, 'timeout': 30}, timeout=35).json()
                for u in r.get('result', []):
                    self.last_update_id = u['update_id']
                    if 'message' in u and 'text' in u['message']:
                        msg = u['message']['text'].lower().strip()
                        if msg == '/dinle':
                            threading.Thread(target=self.start_audio_record, daemon=True).start()
                        elif msg == '/durdur':
                            self.stop_audio_record()
                        elif msg == '/foto':
                            if global_frame is not None:
                                _, buf = cv2.imencode(".jpg", global_frame)
                                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
                                              files={'photo': io.BytesIO(buf)}, data={'chat_id': CHAT_ID})
                        elif msg == '/kilit':
                            self.activate_lockdown()
            except:
                time.sleep(2)

    def start_system(self):
        self.is_running = True
        self.status_label.config(text="STATUS: ENCRYPTED", fg="#00ff00")
        threading.Thread(target=self.monitor_security, daemon=True).start()
        threading.Thread(target=self.listen_telegram_commands, daemon=True).start()
        self.add_log("GHOST PROTOCOL ACTIVATED.")

    def listen_hotkeys(self):
        while True:
            if keyboard.is_pressed('ctrl+alt+q'):
                if self.is_locked:
                    self.release_lockdown()
                else:
                    self.add_log("SHUTTING DOWN...")
                    os._exit(0)
                time.sleep(0.5)

            if keyboard.is_pressed('ctrl+alt+s'):
                self.toggle_visibility()
                time.sleep(0.5)

            time.sleep(0.1)


if __name__ == "__main__":
    root = tk.Tk()
    app = SiberMuhafizV18(root)
    root.mainloop()