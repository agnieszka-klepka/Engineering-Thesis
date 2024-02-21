from model_database import ModelDatabase
import numpy as np


db_handler = ModelDatabase()
sequences, labels = [], []
poses = np.array(
            ["both-legs_standing", "one-leg_standing", "hands-up_standing", "hands-up-one-leg_standing"])

label_map = {label: num for num, label in enumerate(poses)}
print(label_map)

for pose in poses:
    for keypoints in db_handler.getKeypoints(pose):
        sequences.append(keypoints)
        # print(len(keypoints))
        # for k in keypoints:
            # print(len([np.frombuffer(k, dtype=np.float64) for k in keypoints][0]))
        labels.append(label_map[pose])

print(labels)

# for s in sequences:
#     print(f"{s}\n")
#     print(len(s))
# print(len(sequences))
# for _ in range(len(sequences)):
#     labels.append(label_map[poses[0]])
# print(labels)
# print(len(labels))
