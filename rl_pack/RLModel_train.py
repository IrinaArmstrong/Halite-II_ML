import os
from envs import halite_env

from rl.agents import DDPGAgent
from rl.memory import SequentialMemory
from rl.callbacks import ModelIntervalCheckpoint, TrainEpisodeLogger
from rl.random import OrnsteinUhlenbeckProcess
from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import Adam, SGD

from rl_pack.Actor import Actor
from rl_pack.Critic import Critic
from rl_pack.TensorboardHandler import TensorBoard

class Trainer:

    def __init__(self, pre_trained: bool, model_checkpoint_path: str="../models/model_v0"):
        self._pre_trained = pre_trained
        self._env = halite_env.HaliteIIEnv(stdio=True, replay=False)
        self._is_fitted = False
        if self._pre_trained:
            self.actor = load_model(model_checkpoint_path + '_actor.hd5')
            self.critic = load_model(model_checkpoint_path + '_critic.hd5')
        else:
            self.actor = Actor(n_actions=self._env.action_space, n_observations=self._env.observation_space).get_model()
            self.critic, self.action_input = Critic(n_actions=self._env.action_space,
                                                    n_observations=self._env.observation_space).get_model()


    def train(self, nb_steps: int, to_evaluate: bool,
              dump_path="../models", dump_fn="model_v0"):

        nb_steps_warmup = int(nb_steps * 0.01)
        memory = SequentialMemory(limit=10_000, window_length=1)
        random_process = OrnsteinUhlenbeckProcess(size=self._env.action_space, theta=0.15, mu=0.0, sigma=0.3)
        self.agent = DDPGAgent(nb_actions=self._env.action_space,
                          actor=self.actor, critic=self.critic,
                          critic_action_input=self.action_input,
                          memory=memory, nb_steps_warmup_critic=nb_steps_warmup,
                          nb_steps_warmup_actor=nb_steps_warmup,
                          random_process=random_process, gamma=0.9, target_model_update=1e-3)
        self.agent.compile(SGD(lr=1e-5, clipvalue=0.001), metrics=['mae'])
        callbacks = [
            ModelIntervalCheckpoint(os.path.join(dump_path, dump_fn + '_{step}.hd5'), interval=10_000),
            TrainEpisodeLogger(),
            TensorBoard()
        ]
        self.agent.fit(self._env, nb_steps=nb_steps, visualize=False, verbose=2, callbacks=callbacks)
        if to_evaluate:
            self.agent.test(self._env, nb_episodes=1, visualize=False)
        self._is_fitted = True
        self.save(dump_path, dump_fn)


    def evaluate(self):
        self.agent.test(self._env, nb_episodes=1, visualize=False)


    def save(self, model_dump_path="../models",
             model_save_fn="model_v0"):
        self.agent.save_weights('ddpg_{}_weights.h5f'.format(model_save_fn), overwrite=True)
        self.actor.save(os.path.join(model_dump_path, model_save_fn + '_actor.hd5'))
        self.critic.save(os.path.join(model_dump_path, model_save_fn + '_critic.hd5'))


if __name__ == "__main__":
    t = Trainer(pre_trained=False)
    t.train(nb_steps=20_000, to_evaluate=True, )

