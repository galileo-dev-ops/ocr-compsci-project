import numpy as np
from typing import List
import tensorflow as tf

class NeuralPathfinder:
    def __init__(self, rows: int = 6, cols: int = 6):
        self.rows = rows
        self.cols = cols
        self.model = self._build_model()

    def _build_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(4,)),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(4, activation='softmax')
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy')
        return model

    def find_path(self, start: int, end: int) -> List[int]:
        current = start
        path = [current]
        
        while current != end and len(path) < self.rows * self.cols:
            state = self._get_state(current, end)
            action = self._predict_move(state)
            current = self._take_action(current, action)
            path.append(current)
            
        return path if path[-1] == end else []

    def _get_state(self, current: int, end: int) -> np.ndarray:
        current_pos = ((current - 1) // self.cols, (current - 1) % self.cols)
        end_pos = ((end - 1) // self.cols, (end - 1) % self.cols)
        return np.array([current_pos[0], current_pos[1], end_pos[0], end_pos[1]])

    def _predict_move(self, state: np.ndarray) -> int:
        prediction = self.model.predict(state.reshape(1, -1))[0]
        return np.argmax(prediction)

    def _take_action(self, current: int, action: int) -> int:
        row = (current - 1) // self.cols
        col = (current - 1) % self.cols
        
        moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        new_row = row + moves[action][0]
        new_col = col + moves[action][1]
        
        if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
            return new_row * self.cols + new_col + 1
        return current