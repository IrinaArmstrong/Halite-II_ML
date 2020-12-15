from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Activation, Flatten, Concatenate, Input


class Critic:

    def __init__(self, n_actions: int, n_observations: int):
        self._n_actions = n_actions
        self._n_observations = n_observations
        self._model, self._action_input = self.create_model(verbose=True)

    def get_model(self):
        return self._model, self._action_input

    def create_model(self, verbose: bool):
        action_input = Input(shape=(self._n_actions,), name='action_input')
        observation_input = Input(shape=(1,) + self._n_observations.shape, name='observation_input')
        flattened_observation = Flatten()(observation_input)

        x = Dense(400)(flattened_observation)
        x = Activation('relu')(x)
        x = Concatenate()([x, action_input])
        x = Dense(300)(x)
        x = Activation('relu')(x)
        x = Dense(1)(x)
        x = Activation('linear')(x)
        critic = Model(inputs=[action_input, observation_input], outputs=x)
        if verbose:
            print("Critic model created:")
            print(critic.summary())

        return critic, action_input