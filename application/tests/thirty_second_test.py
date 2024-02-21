from keras.models import Sequential
from keras.layers import LSTM, Dense
from keras.metrics import CategoricalAccuracy, Recall
import cv2
import customtkinter
import tkinter
from PIL import Image, ImageTk
import tkinter as tk
import mediapipe as mp
import numpy as np
from functions import sequences, predict_class_with_threshold, draw_landmarks, correct_arrays_of_landmarks, \
    mediapipe_detection
from tests.time_thread import TimerThread
from datetime import datetime

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils


class ThirtySecondsTest(customtkinter.CTkToplevel):
    def __init__(self, master, pose, path, **kwargs):
        super().__init__(master)

        self.cap = cv2.VideoCapture(0)
        self.model = Sequential()
        self.poses = np.array(
            ["both-legs_standing", "one-leg_standing", "hands-up_standing", "hands-up-one-leg_standing"])
        self.pose = pose
        self.current_pose = ""
        self.time_running = False
        self.detections = 0
        self.wrong_detection = 0
        self.max_time = 10

        self.test_started = False
        self.sequence = []
        self.current_image = None
        self.keypoints = None
        self.image = None
        self.ended_tests = []

        self.title(f"{pose.upper()}")
        self.geometry("1300x850")

        frame = customtkinter.CTkFrame(self, width=250, height=400, corner_radius=0, fg_color="#FFFFFF")
        frame.grid(padx=10, pady=10, sticky="nsew")

        self.label = tkinter.Label(frame, text="HEJ! PRZYGOTUJ SIĘ. KLIKNIJ START, BY ZACZĄC TEST",
                                   font=("Arial", 14))
        self.label.grid(row=0, column=0, columnspan=2, pady=10)

        self.panel = tk.Label(frame)
        self.panel.grid(row=1, column=0, columnspan=2, sticky="nsew")

        start_test_button = customtkinter.CTkButton(frame, text="START",
                                                    command=self.start_test,
                                                    corner_radius=0,
                                                    width=75, height=35, fg_color="#FFFFFF", text_color="#4C7DBA",
                                                    border_color="#4C7DBA", border_width=2)
        start_test_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        stop_test_button = customtkinter.CTkButton(frame, text="STOP",
                                                   command=self.destructor,
                                                   corner_radius=0,
                                                   width=75, height=35, fg_color="#FFFFFF", text_color="#4C7DBA",
                                                   border_color="#4C7DBA", border_width=2)
        stop_test_button.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        self.setup_model(path)
        self.video_loop()

    def video_loop(self):
        with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            while self.cap.isOpened():
                ret, frame = self.cap.read()

                if not ret:
                    break
                try:
                    self.image, results = mediapipe_detection(frame, holistic)
                    self.keypoints = correct_arrays_of_landmarks(results)
                    draw_landmarks(self.image, results)

                    cv2image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGBA)

                    self.current_image = Image.fromarray(cv2image)

                    imgtk = ImageTk.PhotoImage(image=self.current_image)
                    self.panel.imgtk = imgtk
                    self.panel.config(image=imgtk)

                    if self.test_started:
                        self.sequence.append(self.keypoints)
                        sequence = self.sequence[-30:]

                        if len(sequence) == 30:
                            self.use_trained_model(sequence)

                    self.update()
                except RuntimeError as e:
                    print("RuntimeError: Too early to create image: no default root window")

    def use_trained_model(self, sequence):
        """
        Zadeklarowany jest ponownie wykorzystywany model, następnie zaciągnięte są
        wagi uzyskane w procesie uczenia w klasie DataProccesor(). Następnie za
        pomocą kamery pobierane są współrzędne ułożenia ciała i za pomocą funkcji
        self.model.predict() sprawdzana jest zgodność.
        """
        threshold = 0.8

        result = self.model.predict(np.expand_dims(sequence, axis=0))[0]
        # print(result)
        prediction = predict_class_with_threshold(result, threshold)
        # print(prediction)
        if prediction == 4:
            self.current_pose = "no-pose-detected"
        else:
            self.current_pose = self.poses[prediction]
        print(self.current_pose)

        # Wykryto pozę pożądana i utworzony zostaje wątek z odliczaniem czasu
        if self.current_pose == self.pose and not self.time_running:
            self.label.config(text="WYKRYTO POZĘ, WYTRZYMAJ W POZYCJI NASTĘPNE 30 SEKUND. CZAS START")
            print("------------------------------------------------------------------------------"
                  "----------------------------------------------------------------------------")
            print("WĄTEK WYSTARTOWAŁ")
            self.thread = TimerThread(max_time=self.max_time)
            self.thread.start()
            self.time_running = True
            self.detections += 1
        # Wciąż wykrywana jest dobra poza i wątek nie jest zatrzymany
        elif self.current_pose == self.pose.lower() and self.time_running:
            if self.thread.test_passed and self.thread.test_passed == True and self.thread.elapsed_time == self.max_time:
                self.label.config(text=f"TEST ZAKOŃCZYŁ SIĘ POMYŚLNIE, MOŻESZ KLIKNĄĆ PRZYCISK STOP")
                print("TEST ZAKONCZONY POMYŚLNIE")
                self.ended_tests.append([datetime.now(), True])
                self.restart_parameters()
                return

            self.label.config(text=f"POZA JEST WYKRYWANA, TEST TRWA, {self.thread.elapsed_time}")
            print("------------------------------------------------------------------------------"
                  "----------------------------------------------------------------------------")
            print("POZA JEST WYKRYWANA")
            self.detections += 1
        # Pożądana poza przestaje być wykrywana i teraz sprawdzane jest czy test należy już zatrzymać
        elif self.current_pose.lower() != self.pose.lower() and self.time_running:
            if (self.detections - self.wrong_detection) < 5:
                self.label.config(
                    text=f"TEST ZOSTAŁ ZATRZYMANY W {self.thread.elapsed_time} SEKUNDZIE, NACIŚNIJ START, BY ZACZĄĆ PONOWNIE LUB STOP, BY SKOŃCZYĆ")
                self.ended_tests.append([datetime.now(), False])
                self.restart_parameters()
                return

            self.detections += 1
            self.wrong_detection = self.detections
        # Warunek podczas ustawiania się do pozy
        else:
            self.label.config(text="POZA NIE ZOSTAŁA JESZCZE WYKRYTA, UPEWNIJ SIĘ, ŻE NA EKRANIE WIDAĆ CAŁĄ SYLWETKĘ")

    def setup_model(self, path):
        self.model.add(
            LSTM(64, return_sequences=True, activation='relu', input_shape=(sequences, 1536)))
        self.model.add(LSTM(128, return_sequences=True, activation='relu'))
        self.model.add(LSTM(64, return_sequences=False, activation='relu'))
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dense(32, activation='relu'))
        self.model.add(Dense(self.poses.shape[0], activation='softmax'))

        self.model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=[CategoricalAccuracy(), Recall()])

        self.model.load_weights(path)

    def start_test(self):
        self.test_started = True
        self.label.config(text="ROZPOCZYNAMY TEST, CZAS BĘDZIE LICZONY OD MOMENTU WYKRYCIA POPRAWNEJ POZYCJI")

    def restart_parameters(self):
        self.thread.stop()
        self.thread.join()
        self.test_started = False
        self.time_running = False
        self.detections = 0
        self.wrong_detection = 0
        self.current_pose = ""

    def destructor(self):
        self.test_started = False
        self.destroy()
        self.cap.release()
        cv2.destroyAllWindows()
