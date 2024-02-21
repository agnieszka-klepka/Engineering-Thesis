from sklearn.model_selection import train_test_split
import tensorflow as tf
from keras.utils import to_categorical
from keras.metrics import CategoricalAccuracy, AUC
from keras.models import Sequential
from keras.layers import LSTM, Dense
from keras.callbacks import TensorBoard
from keras.optimizers import SGD, RMSprop, Adam, Adadelta, Adafactor, Adagrad, Adamax, Nadam, Ftrl
from tensorflow_addons.optimizers import AdamW  # pip install tensorflow-addons
from functions import sequences, sequence_lenght, poses
import numpy as np
import mediapipe as mp
import os
from model_database import ModelDatabase
import random

mp_holistic = mp.solutions.holistic


"""
    Klasa DataProcessor ma za zadanie trenować model danymi przetworzonymi w 
    funkcji powyżej oraz zebranymi w klasie HolisticDataCollector.
    
    Model Sequential() jest jedną z głównych klas biblioteki Keras. Wykorzystuję 
    ją do tworzenia modelu zawierającego wiele warstw układanych sekwencyjnie. 
    Model, który chce stworzyć będzie miał za zadanie klasyfikować poszczególne 
    dane zbierane za pomocą modelu MediaPipe do poszczególnych póz. Jest to 
    rekurencyjna sieć neuronowa z wykorzystaniem architektury LSTM.

    Do modelu za pomocą funkcji add() są dodawane warstwy. Pierwsze trzy warstwy 
    są warstwami LSTM - pierwsza o rozmiarze 64, druga o rozmiarze 128 i trzecia 
    ponownie 64. Trzecia warstwa,  w przeciwieństwie do dwóch poprzednich, nie 
    zwraca sekwencji wyników, tylko wynik z ostatniego kroku, ponieważ chcemy 
    przewidzieć jedną wartość na końcu. Zapobiega to również rozbudowywaniu modelu 
    i komplikowaniu go. Warstwa BatchNormalization zapewnia normalizację wsadową, 
    redukcję wewnętrznego gradientu, stabilizuje i przyspiesza uczenie. 

    Funkcją aktywacji jest ReLU (Rectified Linear Activation). Funkcja sprawdza 
    się w treningu sieci i jest bardzo skuteczna. W ostatniej warstwie używana 
    jest funkcja softmax, która użyta jest do ostatecznej klasyfikacji.
"""


class DataProccesor():
    def __init__(self):
        log_dir = os.path.join('logs')
        self.tb_callback = TensorBoard(log_dir=log_dir)
        self.__X_train, self.__X_test, self.__y_train, self.__y_test = self.data_split()
        self.model = Sequential()

    def train_model(self):
        self.model.add(
            LSTM(96, return_sequences=True, activation='relu', input_shape=(sequences, 1536)))
        self.model.add(LSTM(160, return_sequences=True, activation='relu'))
        self.model.add(LSTM(96, return_sequences=False, activation='relu'))
        self.model.add(Dense(96, activation='relu'))
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dense(poses.shape[0], activation='softmax'))

        # optymalizatory
        # self.model.compile(optimizer=SGD(learning_rate=0.0001, momentum=0.7, nesterov=True), loss='categorical_crossentropy', metrics=[CategoricalAccuracy(), AUC()])
        # self.model.compile(optimizer=RMSprop(learning_rate=0.0001, decay=1e-12), loss='categorical_crossentropy', metrics=[CategoricalAccuracy(), AUC()])
        # self.model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=[CategoricalAccuracy(), AUC()])
        # self.model.compile(optimizer=AdamW(learning_rate=0.0001, weight_decay=1e-6), loss='categorical_crossentropy', metrics=[CategoricalAccuracy(), AUC()])
        # self.model.compile(optimizer=Adadelta(), loss='categorical_crossentropy', metrics=[CategoricalAccuracy(), AUC()])
        # self.model.compile(optimizer=Adagrad(), loss='categorical_crossentropy', metrics=[CategoricalAccuracy(), AUC()])
        self.model.compile(optimizer=Adamax(), loss='categorical_crossentropy', metrics=[CategoricalAccuracy(), AUC()])
        # self.model.compile(optimizer=Adafactor(learning_rate=0.1, beta_2_decay=-0.2), loss='categorical_crossentropy', metrics=[CategoricalAccuracy(), AUC()])
        # self.model.compile(optimizer=Nadam(learning_rate=0.0001, decay=1e-8), loss='categorical_crossentropy', metrics=[CategoricalAccuracy(), AUC()])
        # self.model.compile(optimizer=Ftrl(), loss='categorical_crossentropy', metrics=[CategoricalAccuracy(), AUC()])

        self.model.fit(self.__X_train, self.__y_train, epochs=800,
                       callbacks=[self.tb_callback])  # tu mozna callback na koncowym etapie wykreślić

        tf.summary.scalar('Accuracy', self.model.metrics[0].result().numpy(), description='Training Accuracy')
        tf.summary.scalar('AUC', self.model.metrics[1].result().numpy(), description='Training AUC')

        self.model.summary()

        """
            Poniższa linijka zapisują wagi naszego wyuczonego modelu. Sprawdzane jest 
            przedtem, czy plik z wagami już istnieje, jest to potrzebne przy uczeniu modelu 
            i dostosowywaniu paramentrów.
        """
        if os.path.exists('weights/weights.h5'):
            rand = random.randint(1, 1000)
            os.rename('weights/weights.h5', f'weights/old_weights{rand}.h5')

        self.model.save_weights('weights/weights.h5')

    """
        Funkcja data_split() ma za zadanie przygotować dane pozystane za pomocą klasy 
        HolisticDataCollector(). Na początku mapowane są pozy, dla których zbierane 
        są dane. Następnie iterując po danych rozdzielam je na zbiór danych wejściowych 
        - z danymi oraz na zbiór z wynikami - czyli etykiety. Za pomocą wbudowanej 
        funkcji z sklearn - train_test_split - zbiór wszystkich danych wejściowych 
        i wyjściowych jest dzielony na zbiory trenujące oraz zbiory testujące.
    """

    def data_split(self):
        sequences, labels = [], []  # listy zawierające dane wejściowe oraz wyjściowe
        temp = []

        label_map = {label: num for num, label in
                     enumerate(poses)}  # numeruje pozy w listy poses za pomocą funkcji enumerate

        db_handler = ModelDatabase()

        for pose in poses:
            keypoints = []
            for kp in db_handler.getKeypoints(pose):
                for k in kp:
                    keypoints.append(np.frombuffer(k, dtype=np.float64)) # dane wyciągane z bazy jako wartości binarne - wymagają konwersji
            for i in range(0, len(keypoints), sequence_lenght):
                sequence = keypoints[i:i + sequence_lenght]
                if len(sequence) == sequence_lenght:
                    sequences.append(sequence)
                labels.append(label_map[pose])

        X = np.array(sequences)  # input data
        y = to_categorical(labels).astype(int)  # outputs

        X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                            test_size=0.05)  # podział danych na zbiory trenujące oraz testujące

        return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    processor = DataProccesor()
    processor.train_model()
