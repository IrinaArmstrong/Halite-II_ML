import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Flatten, Input, Concatenate
from tensorflow.keras.optimizers import Adam

class Actor:

    def __init__(self, n_actions: int, n_observations: int):
        self._n_actions = n_actions
        self._n_observations = n_observations
        self._model = self.create_model(verbose=True)


    def get_model(self):
        return self._model

    def create_model(self, verbose: bool):
        # Next, we build a very simple model.
        actor = Sequential()
        actor.add(Flatten(input_shape=(1,) + self._n_observations.shape))
        actor.add(Dense(400))
        actor.add(Activation('relu'))
        actor.add(Dense(300))
        actor.add(Activation('relu'))
        actor.add(Dense(self._n_actions))
        actor.add(Activation('tanh'))
        if verbose:
            print("Actor model created:")
            print(actor.summary())
        return actor