from keras.models import Sequential
from keras.layers import LSTM, Dense, BatchNormalization
from keras.metrics import CategoricalAccuracy, Recall
import cv2
import mediapipe as mp
import numpy as np
from data_collector import HolisticDataCollector
from functions import sequences, poses, mediapipe_detection, draw_landmarks, correct_arrays_of_landmarks

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils


class TrainedModel():
    """
    W klasie TrainedModel wykorzystywane są wagi pozyskane w procesie uczenia.
    """

    def __init__(self):
        """
        Przy deklarowaniu samej klasy deklarowany jest obiekt kolektora.

        """
        self.collector = HolisticDataCollector()
        self.model = Sequential()
        self.sequences = 30
        self.colors = [(245, 117, 16), (117, 245, 16), (16, 117, 245)]
        self.current_pose = ""

    def use_trained_model(self):
        """
        Zadeklarowany jest ponownie wykorzystywany model, następnie zaciągnięte są
        wagi uzyskane w procesie uczenia w klasie DataProccesor(). Następnie za
        pomocą kamery pobierane są współrzędne ułożenia ciała i za pomocą funkcji
        self.model.predict() sprawdzana jest zgodność
        """
        sequence = []
        threshold = 0.8

        self.model.add(
            LSTM(64, return_sequences=True, activation='relu', input_shape=(sequences, 1536)))
        self.model.add(LSTM(128, return_sequences=True, activation='relu'))
        self.model.add(LSTM(64, return_sequences=False, activation='relu'))
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dense(32, activation='relu'))
        self.model.add(Dense(poses.shape[0], activation='softmax'))

        self.model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=[CategoricalAccuracy(), Recall()])

        self.model.load_weights('weights/weights.h5')

        cap = cv2.VideoCapture(0)
        with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            while cap.isOpened():

                ret, frame = cap.read()

                image, results = mediapipe_detection(frame, holistic)

                draw_landmarks(image, results)

                keypoints = correct_arrays_of_landmarks(results)

                sequence.append(keypoints)
                sequence = sequence[-30:]

                if len(sequence) == 30:
                    res = self.model.predict(np.expand_dims(sequence, axis=0))[0]

                    if res[np.argmax(res)] > threshold:
                        self.current_pose = poses[np.argmax(res)].upper()
                        cv2.putText(image, self.current_pose, (6, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA) # 255 255 255

                cv2.imshow('Recognizing Pose', image)

                if cv2.waitKey(10) == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    processor = TrainedModel()
    processor.use_trained_model()
