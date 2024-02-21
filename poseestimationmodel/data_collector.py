import cv2
import numpy as np
import mediapipe as mp
from model_database import ModelDatabase
from functions import mediapipe_detection, draw_landmarks, correct_arrays_of_landmarks, sequences, sequence_lenght, poses

mp_holistic = mp.solutions.holistic


class HolisticDataCollector:
    """
    W klasie HolisticDataCollector() znajduje się funkcja __init__(), w której definiuję
    zmienne używane w klasie i definiujące ją. Jest to klasa, która służy zbieraniu danych
    do uczenia modelu. Za pomocą MediaPipe wykrywana jest sylwetka oraz punty
    charakterystyczne, które pozwolą później nauczyć model.
    """

    def __init__(self):
        self.__db_handler = ModelDatabase()

        self.holistic = mp_holistic.Holistic(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def process_video(self):
        # """
        # Metoda process_video() na początku zawiera pętle, dzięki którym tworzą się
        # odpowiednie katalogi na zbieranie danych. Następnie za pomocą kamery
        # zbierane są współrzędne
        # """
        cap = cv2.VideoCapture(0)
        stop_flag = False

        # """
        #     Collecting landmarks of poses in a loop:
        #         - each pose has amount of sequences recording planed
        #         - each video amount of sequences frames
        #         - each frame has array of 1662 keypoint
        # """
        while not stop_flag:
            print("Witam, proszę podaj pozę, dla której chcesz nagrać dane.\n Do wyboru masz:\n - stanie na obu "
                  "nogach - 0\n - stanie na jednej nodze - 1\n - stanie na dwóch nogach z rękami w górze - 2\n "
                  "- stanie na jednej nodze z rękami w górze - 3\n Jeżeli chcesz zakończyć wpisz polecenie STOP\n")
            data = input("Twój wybór: ")

            if data.lower() == "stop":
                stop_flag = True
            else:
                pose = poses[int(data)]
                for sequence in range(sequences):
                    for frame_num in range(sequence_lenght):
                        success, frame = cap.read()
                        if not success:
                            print("Ignoring empty camera frame.")
                            continue

                        height, width, _ = frame.shape
                        left_margin = 350
                        right_margin = width - 350

                        mask = frame.copy()
                        mask[:, :left_margin] = 0
                        mask[:, right_margin:] = 0

                        resized_image = cv2.addWeighted(frame, 1, mask, 0.5, 0)

                        image, results = mediapipe_detection(resized_image, self.holistic)
                        draw_landmarks(image, results)

                        if frame_num == 0:
                            cv2.putText(image, 'NAGRYWANIE ROZPOCZNIE SIE ZA 5 SEKUND', (120, 200),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 4, cv2.LINE_AA)
                            cv2.putText(image, 'Zbieram ramkę {} Numer wideo {}'.format(pose, sequence),
                                        (15, 12),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4, cv2.LINE_AA)
                            cv2.imshow('MediaPipe Holistic Kolekcjonowanie Danych', image)
                            cv2.waitKey(1000)
                        else:
                            cv2.putText(image, 'Zbieram ramkę {} Numer wideo {}'.format(pose, sequence),
                                        (15, 12),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4, cv2.LINE_AA)
                            cv2.imshow('MediaPipe Holistic Kolekcjonowanie Danych', image)

                        # saving arrays to directories
                        keypoints = correct_arrays_of_landmarks(results)

                        self.__db_handler.saveKeypoints(pose, keypoints)

                        if cv2.waitKey(5) == ord('q'):
                            break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    collector = HolisticDataCollector()
    collector.process_video()
