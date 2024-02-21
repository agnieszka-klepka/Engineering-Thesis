import cv2
import numpy as np
import mediapipe as mp
from datetime import datetime

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils


def mediapipe_detection(image, model):
    """
    Funkcja mediapipe_detection() przyjmuje dwa argumenty, image - czyli obraz z kamery,
    który chcemy przetworzyć oraz model - model ML z biblioteki MediaPipe, z którego
    chcemy korzystać. Wyniki przetwarzania (współrzędne rozpoznanych częsci ciała) zapisywane
    są do zmiennej results, która razem ze zmienna image zwracana jest w funkcji
    """
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = model.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image, results


def draw_landmarks(image, results):
    """
    Funkcja draw_landmarks() służy do rysowaniu punktów charakterystycznych oraz połączeń na
    rozpoznawanym obrazie.
    """
    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_TESSELATION,
                              mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
                              mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1)
                              )
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2))


def correct_arrays_of_landmarks(results):
    """
    Funkcja correct_arrays_of_landmarks() zwraca listę koordynatów wykrytych elementów całej
    pozy. Lista jest uzupełniona o zera, jeżeli część
    ciała nie znajduje się w zasięgu kamery.
    Charakterystyczne punkty niewidocznych części ciała na kamerze są równe None
    Zwraca tablicę zer, jeśli część ciała nie jest widoczna na kamerze
    """
    face = np.array(
        [[res.x, res.y, res.z] for res in
         results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(
        1404)  # 468 landmarks multiple 3 values
    pose = np.array([[result.x, result.y, result.z, result.visibility] for result in
                     results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(
        132)  # 33 landmarks multiple 4 values

    return np.concatenate([pose, face])


def predict_class_with_threshold(predictions, threshold):
    classes_above_threshold = np.where(predictions > threshold)[0]
    if len(classes_above_threshold) == 0:
        return 4

    return classes_above_threshold[np.argmax(predictions[classes_above_threshold])]


def date_from_db(date_string):
    data_obj = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f')
    data_czas_bez_milisekund = data_obj.strftime('%Y-%m-%d %H:%M:%S')
    return data_czas_bez_milisekund


def test_name_from_db(test_name):
    pl_poses = ["Stanie na dwóch nogach", "Stanie na jednej nodze", "Stanie z rękami w górze", "Stanie na jednej nodze z rękami w górze", "Siadanie i wstawanie"]
    poses = np.array(
        ["both-legs_standing", "one-leg_standing", "hands-up_standing", "hands-up-one-leg_standing", "squad"])
    pose = 0
    for x in range(len(poses)):
        if test_name == poses[x]:
            pose = x
    return pl_poses[pose]


def test_result_from_db(test_result):
    if test_result == '1':
        return "Pozytywny"
    elif test_result == '0':
        return "Negatywny"
