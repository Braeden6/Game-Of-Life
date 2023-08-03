import numpy as np
import tensorflow as tf
from tensorflow import keras

class NeuralNetwork:
    def __init__(self, state_size, action_size, batch_size = 128, epsilon = 1, learning_rate = 0.001):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.model = self._build_model()
        self.epsilon = epsilon
        self.batch_size = batch_size

    def _build_model(self):
        init = tf.keras.initializers.HeUniform()
        model = keras.Sequential()
        model.add(keras.layers.Flatten(input_shape=self.state_size))
        model.add(keras.layers.Dense(30, activation='relu', kernel_initializer=init))
        model.add(keras.layers.Dense(self.action_size))
        model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), optimizer='adam', metrics=['accuracy'])
        return model

    def act(self, observation):  
        #if np.random.rand() <= self.epsilon:
        #    return random.randrange(self.action_size)
        return self.model.predict(observation)

    def train(self, X , Y):
        self.model.fit(X, Y, epochs=10)
    
    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)
