import gc
import itertools
import numpy as np
from copy import deepcopy
from numpy.random import uniform, seed

import config.config_sys as cfg_sys
from algorithms.heuristic import alg
from algorithms.utils import totalDelay
from code_utils.ddqn import DDQNAgent
from code_utils.utils import getLogger
from config.config_ctlr import cfg_ctlr
from generator import generator

logger = getLogger(name='rl')
getLogger().setLevel('CRITICAL')


class Env:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.reset()

    def reset(self, state=None):
        self.state = uniform(low=-1, high=1, size=3) if state is None else state
        self.value = totalDelay(
            assignment=alg(w1=self.state[0], w2=self.state[1], w3=self.state[2], **self.kwargs),
            delayMat=self.kwargs['delayMat'],
            userSet=self.kwargs['userSet']
        )
        logger.critical('env reset: state: %s', str(self.state))

    def step(self, action):
        self.state = self.actionMap(self.state, action)
        newValue = totalDelay(
            assignment=alg(w1=self.state[0], w2=self.state[1], w3=self.state[2], **self.kwargs),
            delayMat=self.kwargs['delayMat'],
            userSet=self.kwargs['userSet']
        )
        reward = self.value - newValue
        self.value = newValue
        return self.state, reward

    def getState(self):
        return self.state

    @staticmethod
    def actionMap(state, action):
        direction = [0, 0]
        direction[0] = action % 3
        direction[1] = action // 3
        direction = list(map(lambda x: (x - 1) / 10, direction))
        state = deepcopy(state)
        state[0] += direction[0]
        state[1] += direction[1]
        state[2] = 1 - state[0] - state[1]
        return state


class Model:
    def __init__(self, **kwargs):
        self.env = Env(**kwargs)
        self.agent = DDQNAgent(
            alpha=0.02,
            gamma=0.98,
            n_actions=9,
            epsilon=0.95,
            batch_size=64,
            input_dims=3,
            epsilon_dec=0.994
        )

    def save(self):
        self.agent.save_model()

    def load(self):
        self.agent.load_model()

    def train(self, episode=100000):
        for i_episode in itertools.count(start=0):
            if i_episode % 10 == 0:
                logger.critical(
                    'model: episode: %d, current state: %s, epsilon: %.3f',
                    i_episode,
                    str(self.env.getState()),
                    self.agent.epsilon
                )
            if i_episode % 100 == 0:
                self.env.reset()
                gc.collect()

            if i_episode % 100 == 0:
                self.agent.learn()
                # self.agent.update_network_parameters()

            if i_episode > 0 and (i_episode % 1000 == 0):
                self.save()

            if i_episode > 0 and (i_episode % 1000 == 0):
                st, rewards = self.test(state=[0.3, 0.3, 0.4])
                print(st, rewards)
                self.env.reset()

            if i_episode == episode:
                break

            # train
            state = self.env.getState()
            action = self.agent.choose_action(state=state)
            newState, reward = self.env.step(action)
            self.agent.remember(
                state=state,
                action=action,
                reward=reward,
                new_state=newState,
                done=False
            )
            # print(reward)
            pass

    def test(self, state, steps=100):
        state = np.array(state)
        self.env.reset(state=state)
        rewards = 0
        for _ in range(steps):
            action = self.agent.choose_action_no_explore(state=state)
            state, reward = self.env.step(action=action)
            rewards += reward
        return state, rewards


if __name__ == '__main__':
    seed(cfg_sys.RANDOM_SEED)
    userSet, dcSet = generator(nodeSet=cfg_ctlr['topo']['nodeSet'], serviceSet=cfg_ctlr['serviceSet'])
    delayMat = {
        '134.122.119.166': {'134.122.119.166': 0.02, '143.198.219.100': 237.94, '143.198.64.134': 75.14},
        '143.198.64.134': {'134.122.119.166': 75.23, '143.198.219.100': 163.84, '143.198.64.134': 0.01},
        '143.198.219.100': {'134.122.119.166': 238.3, '143.198.219.100': 0.01, '143.198.64.134': 163.82}
    }
    model = Model(
        userSet=userSet,
        dcSet=dcSet,
        nodeSet=cfg_ctlr['topo']['nodeSet'],
        edgeList=cfg_ctlr['topo']['edgeList'],
        serviceSet=cfg_ctlr['serviceSet'],
        delayMat=delayMat,
        budget=cfg_ctlr['budget']
    )
    model.load()
    model.train()
    st, rewards = model.test(state=[0.3, 0.3, 0.4])
    print(st, rewards)
