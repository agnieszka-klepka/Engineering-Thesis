from .functions import mediapipe_detection, draw_landmarks, correct_arrays_of_landmarks, predict_class_with_threshold
from .functions import date_from_db, test_name_from_db, test_result_from_db
import numpy as np

sequences = 30
sequence_lenght = 30
poses = np.array(
            ["both-legs_standing", "one-leg_standing", "hands-up_standing", "hands-up-one-leg_standing"])
