import sqlite3


class ModelDatabase:
    def __init__(self):
        self.__conn = sqlite3.connect("pose_data.db")
        self.__cursor = self.__conn.cursor()
        self.__cursor.execute('''
            CREATE TABLE IF NOT EXISTS posedata (
                pose_id INTEGER PRIMARY KEY,
                pose_name TEXT,
                mediapipe_data BLOB
            )
        ''')

    def saveKeypoints(self, pose, keypoints):
        self.__cursor.execute("INSERT INTO posedata (pose_name, mediapipe_data) VALUES (?, ?)",
                              (pose, keypoints))
        self.__conn.commit()

    def getKeypoints(self, pose_name):
        query = "SELECT mediapipe_data FROM posedata WHERE pose_name = ?"
        self.__cursor.execute(query, (pose_name,))
        result = self.__cursor.fetchall()
        return result

    def __del__(self):
        self.__conn.close()
