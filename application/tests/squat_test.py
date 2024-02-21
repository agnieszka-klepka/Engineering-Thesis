import cv2
import mediapipe as mp
import numpy as np
import customtkinter, tkinter
from PIL import Image, ImageTk
from tests.time_thread import TimerThread
from datetime import datetime

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


class SquadTest(customtkinter.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.cap = cv2.VideoCapture(0)

        self.test_started = False
        self.pose_up = False
        self.pose_down = False
        self.max_time = 10
        self.thread = None
        self.ended_tests = []

        self.title("Test dynamiczny - siadanie")
        self.geometry("1300x850")

        frame = customtkinter.CTkFrame(self, width=250, height=400, corner_radius=0, fg_color="#FFFFFF")
        frame.grid(padx=10, pady=10, sticky="nsew")

        self.label = tkinter.Label(frame, text="HEJ! PRZYGOTUJ SIĘ. KLIKNIJ START, BY ZACZĄC TEST",
                                   font=("Arial", 14))
        self.label.grid(row=0, column=0, columnspan=2, pady=10)

        self.panel = tkinter.Label(frame)
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

        self.video_loop()

    def video_loop(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()

            if not ret:
                break
            try:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                results = self.pose.process(image)

                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                          mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4),
                                          mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2))

                cv2image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)

                self.current_image = Image.fromarray(cv2image)

                imgtk = ImageTk.PhotoImage(image=self.current_image)
                self.panel.imgtk = imgtk
                self.panel.config(image=imgtk)

                if self.test_started:
                    self.process_frame(image, results)

                self.update()
            except RuntimeError as e:
                print("RuntimeError: Too early to create image: no default root window")

    def process_frame(self, image, results):

        # LANDMARKS
        # 0 - NOSE 1 - LEFT_EYE_INNER 2 - LEFT_EYE 3 - LEFT_EYE_OUTER 4 - RIGHT_EYE_INNER
        # 5 - RIGHT_EYE 6 - RIGHT_EYE_OUTER 7 - LEFT_EAR 8 - RIGHT_EAR 9 - MOUTH_LEFT 10 - MOUTH_RIGHT
        # 11 - LEFT_SHOULDER 12 - RIGHT_SHOULDER 13 - LEFT_ELBOW 14 - RIGHT_ELBOW 15 - LEFT_WRIST
        # 16 - RIGHT_WRIST 17 - LEFT_PINKY 18 - RIGHT_PINKY 19 - LEFT_INDEX 21 - LEFT_THUMB
        # 22 - RIGHT_THUMB 23 - LEFT_HIP 24 - RIGHT_HIP 25 - LEFT_KNEE 26 - RIGHT_KNEE
        # 27 - LEFT_ANKLE 28 - RIGHT_ANKLE 29 - LEFT_HEEL 30 - RIGHT_HEEL 31 - LEFT_FOOT_INDEX
        # 32 - RIGHT_FOOT_INDEX

        try:
            landmarks = results.pose_landmarks.landmark

            right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                         landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
            right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                           landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

            angle = self.calculate_angle(right_hip, right_knee, right_ankle)

            # jeżeli wcześniej nie była wykryta poza stojąca i siedząca -- test się dopiero zaczyna
            if not self.pose_up and not self.pose_down:
                if angle > 170:
                    print("----------------------------------------")
                    self.pose_up = True
                    self.thread = TimerThread(self.max_time)
                    self.label.config(text="WYKRYTO POSTAWĘ STOJĄCĄ")
            # jezeli wczesniej byla wykryta poza stojąca, teraz oczekujemy siedzącej
            elif self.pose_up and not self.pose_down:
                if self.thread.elapsed_time < self.max_time:
                    if angle < 110:
                        print("----------------------------------------")
                        print("TRUE")
                        self.pose_up = False
                        self.pose_down = True
                        self.label.config(text="WYKRYTO POSTAWĘ SIEDZĄCĄ")
                # czas na wykonanie ćwiczenia się skończył
                else:
                    print("----------------------------------------")
                    print("FALSE")
                    self.label.config(text="TEST ZAKONCZYŁ SIĘ NIEPOMYŚLNIE, SPRÓBUJ PONOWNIE")
                    self.ended_tests.append([datetime.now(), False])
                    self.restart_parameters()
            # jeżeli wcześniej była wykryta poza siedząca i teraz wykryta stojąca
            elif not self.pose_up and self.pose_down:
                if self.thread.elapsed_time < self.max_time:
                    if angle > 170:
                        print("----------------------------------------")
                        print("TRUE")
                        self.label.config(text="TEST ZAKONCZYŁ SIĘ POMYŚLNIE, MOŻESZ KLIKNĄĆ STOP")
                        self.ended_tests.append([datetime.now(), True])
                        self.restart_parameters()
                # jezeli czas na ćwiczenie się skończył
                else:
                    print("----------------------------------------")
                    print("FALSE")
                    self.label.config(text="TEST ZAKONCZYŁ SIĘ NIEPOMYŚLNIE, SPRÓBUJ PONOWNIE")
                    self.ended_tests.append([datetime.now(), False])
                    self.restart_parameters()

            if self.thread:
                print(self.thread.elapsed_time)
            print(angle)

        except:
            pass

    def start_test(self):
        self.test_started = True
        self.label.config(text="ROZPOCZYNAMY TEST, WYKONAJ CWICZENIE W USTAWIENIU BOKIEM")

    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)  # mid coordinate
        c = np.array(c)

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    def restart_parameters(self):
        self.pose_down = False
        self.pose_up = False
        self.test_started = False
        self.thread.stop()
        self.thread.join()

    def destructor(self):
        self.test_started = False
        self.destroy()
        self.cap.release()
        cv2.destroyAllWindows()
