import pickle
import cv2
import mediapipe as mp
import numpy as np
import os
from tkinter import Tk, Label, Button, filedialog, Frame
from PIL import Image, ImageTk
import threading
import pyautogui

# Load the trained sign language model
model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.5)  # Adjusted confidence

# Label Mapping for Sign Language
labels_dict = {0: 'hello', 1: 'i love python', 2:'please' }

class SignLanguageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sign Language Detection")
        self.root.geometry("900x700")

        # GUI Components
        self.video_frame = Label(self.root)
        self.video_frame.pack(pady=10)

        self.prediction_label = Label(self.root, text="Prediction: ", font=("Helvetica", 16))
        self.prediction_label.pack(pady=5)

        self.sentence_label = Label(self.root, text="Sentence: ", font=("Helvetica", 16))
        self.sentence_label.pack(pady=5)

        button_frame = Frame(self.root)
        button_frame.pack(pady=10)

        self.start_button = Button(button_frame, text="Start Detection", command=self.start_detection, font=("Helvetica", 14), bg="lightgreen")
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = Button(button_frame, text="Stop Detection", command=self.stop_detection, font=("Helvetica", 14), bg="lightcoral")
        self.stop_button.grid(row=0, column=1, padx=10)

        self.clear_button = Button(button_frame, text="Clear Sentence", command=self.clear_sentence, font=("Helvetica", 14), bg="lightblue")
        self.clear_button.grid(row=0, column=2, padx=10)

        self.record_button = Button(button_frame, text="Start Recording", command=self.start_recording, font=("Helvetica", 14), bg="orange")
        self.record_button.grid(row=1, column=0, padx=10, pady=10)

        self.stop_record_button = Button(button_frame, text="Stop Recording", command=self.stop_recording, font=("Helvetica", 14), bg="red")
        self.stop_record_button.grid(row=1, column=1, padx=50, pady=10)

        # Video Capture
        self.cap = None
        self.running = False
        self.recording = False
        self.recording_thread = None

        # Sentence Storage
        self.sentence = []
        self.previous_word = None

    def start_detection(self):
        if not self.running:
            self.cap = cv2.VideoCapture(0)
            self.running = True
            self.update_frame()

    def stop_detection(self):
        if self.running:
            self.running = False
            if self.cap:
                self.cap.release()
            self.video_frame.config(image="")
            self.prediction_label.config(text="Prediction: ")

    def clear_sentence(self):
        self.sentence = []
        self.sentence_label.config(text="Sentence: ")

    def update_frame(self):
        if self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                self.stop_detection()
                return

            data_aux, x_, y_ = [], [], []
            H, W, _ = frame.shape
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )
                    for i in range(len(hand_landmarks.landmark)):
                        x = hand_landmarks.landmark[i].x
                        y = hand_landmarks.landmark[i].y
                        x_.append(x)
                        y_.append(y)

                    for i in range(len(hand_landmarks.landmark)):
                        data_aux.append(x - min(x_))
                        data_aux.append(y - min(y_))

                x1 = int(min(x_) * W) - 10
                y1 = int(min(y_) * H) - 10
                x2 = int(max(x_) * W) - 10
                y2 = int(max(y_) * H) - 10

                try:
                    prediction = model.predict([np.asarray(data_aux)])
                    predicted_character = labels_dict[int(prediction[0])]

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
                    cv2.putText(frame, predicted_character, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3, cv2.LINE_AA)

                    # Update GUI
                    self.prediction_label.config(text=f"Prediction: {predicted_character}")

                    # Update sentence if a new sign is detected
                    if predicted_character != self.previous_word:
                        self.sentence.append(predicted_character)
                        self.previous_word = predicted_character
                        self.sentence_label.config(text=f"Sentence: {' '.join(self.sentence)}")

                except Exception as e:
                    self.prediction_label.config(text="Prediction: Error")
                    print(f"Prediction error: {e}")

            # Convert frame to display in Tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame = frame.resize((800, 450), Image.Resampling.LANCZOS)
            frame_tk = ImageTk.PhotoImage(image=frame)

            self.video_frame.imgtk = frame_tk
            self.video_frame.config(image=frame_tk)

            # Schedule the next frame update
            self.video_frame.after(10, self.update_frame)

    def record_screen(self):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".avi",
            filetypes=[("AVI files", "*.avi")],
            title="Save Recording As"
        )
        if not save_path:
            self.recording = False
            return

        screen_size = pyautogui.size()
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(save_path, fourcc, 20.0, screen_size)

        self.record_button.config(text="Recording...", state="disabled")
        try:
            while self.recording:
                img = pyautogui.screenshot()
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                out.write(frame)
        except Exception as e:
            print(f"Recording Error: {e}")
        finally:
            out.release()
            self.record_button.config(text="Start Recording", state="normal")

    def start_recording(self):
        if not self.recording:
            self.recording = True
            self.recording_thread = threading.Thread(target=self.record_screen)
            self.recording_thread.start()

    def stop_recording(self):
        if self.recording:
            self.recording = False
        if self.recording_thread:
            self.recording_thread.join()

# Run the App
root = Tk()
app = SignLanguageApp(root)
root.mainloop()
