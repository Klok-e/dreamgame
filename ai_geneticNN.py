from locals import *
import pygame
import random

from collections import deque
import keras
import numpy as np


class Agent():
    """Represent a network and let us operate on it.
    Currently only works for an MLP.
    """
    gamma = 0.95  # discount rate
    epsilon = 1.0  # exploration rate
    epsilon_min = 0.01
    epsilon_decay = 0.95
    learning_rate = 0.001
    discount_factor = 0.9

    NN_PARAM_CHOICES = {
        'nb_neurons': [8, 16, 32, 64, 128, 256],
        'nb_layers': [1, 2, 3, 4],
        'activation': ['relu', 'elu', 'tanh', 'sigmoid'],
        'optimizer': ['rmsprop', 'adam', 'sgd', 'adagrad',
                      'adadelta', 'adamax', 'nadam'],
    }

    action_size = len(action_choices)

    def __init__(self,state_size):
        """Initialize our network.
        Args:
            nn_param_choices (dict): Parameters for the network, includes:
                nb_neurons (list): [64, 128, 256]
                nb_layers (list): [1, 2, 3, 4]
                activation (list): ['relu', 'elu']
                optimizer (list): ['rmsprop', 'adam']
        """
        self.state_size = state_size

        self.accuracy = 0.

        self.network = self.create_random()
        # print(self.network)

        self.memory = deque(maxlen=1000)

        self.model = self._build_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = keras.models.Sequential()
        for i, l in enumerate(self.network):
            if i == 0:
                neurons = l[0]
                inpdim = l[1]
                activation = l[2]
                model.add(keras.layers.Dense(neurons, input_dim=inpdim, activation=activation))
            elif i == len(self.network) - 1:
                act_size = l[0]
                activation = l[1]
                model.add(keras.layers.Dense(act_size, activation=activation))
            else:
                neurons = l[0]
                activation = l[1]
                model.add(keras.layers.Dense(neurons, activation=activation))

                model.compile(loss='mse',
                              optimizer=keras.optimizers.Adam(lr=self.learning_rate))
        model.summary()
        return model

    def create_random(self):
        """Create a random network.
        It must look like:
        [[8, None, 'relu'],
        [8, 'relu'],
        [None, 'linear']]
        """
        # TODO: not random a little
        randnetwork = []

        #print(self.state_size,self.action_size)
        first = [8, self.state_size, 'relu']
        second = [8, 'relu']
        third = [self.action_size, 'linear']
        randnetwork.append(first)
        randnetwork.append(second)
        randnetwork.append(third)

        return randnetwork

    def memorize(self, state, action, reward, next_state):
        self.memory.append((state, action, reward, next_state))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        #print(act_values,'- values')
        return np.argmax(act_values[0])  # returns action

    def replay(self, batch_size):
        print(self.epsilon)

        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state in minibatch:

            target = reward + self.gamma * np.amax(self.model.predict(next_state)[0])
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.train_on_batch(state, target_f)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def print_network(self):
        """Print out a network."""
        print(self.network)





class Human():
    def __init__(self, crt):
        self.event = None
        self.crt = crt

    def decide(self, variants):
        ans = None
        e = self.event
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                ans = ATTACK
            elif e.key == pygame.K_w:
                ans = K_UP
            elif e.key == pygame.K_a:
                ans = K_LEFT
            elif e.key == pygame.K_d:
                ans = K_RIGHT
            elif e.key == pygame.K_e:
                ans = EAT
        # print(e)
        return ans

    def save_event(self, event):
        self.event = event
