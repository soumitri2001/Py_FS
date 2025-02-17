"""
Programmer: Soumitri Chattopadhyay
Date of Development: 11/07/2021
This code has been developed according to the procedures mentioned in the following research article:
"Laith A., Diabat A., Mirjalili S., Elaziz M.A., Gandomi A.H. The Arithmetic Optimization Algorithm.
Computer Methods in Applied Mechanics and Engineering, 376, 113609 (2021)"
"""

import math

import numpy as np
from sklearn import datasets

from Py_FS.wrapper.nature_inspired.algorithm import Algorithm
from Py_FS.wrapper.nature_inspired._transfer_functions import get_trans_function


class AOA(Algorithm):

    # Arithmetic Optimization Algorithm
    ############################### Parameters ####################################
    #                                                                             #
    #   num_agents: number of agents                                              #
    #   max_iter: maximum number of generations                                   #
    #   train_data: training samples of data                                      #
    #   train_label: class labels for the training samples                        #
    #   obj_function: the function to maximize while doing feature selection      #
    #   trans_function_shape: shape of the transfer function used                 #
    #   save_conv_graph: boolean value for saving convergence graph               #
    #                                                                             #
    ###############################################################################

    def __init__(self,
                 num_agents,
                 max_iter,
                 train_data,
                 train_label,
                 save_conv_graph=False,
                 seed=0):

        super().__init__(num_agents=num_agents,
                         max_iter=max_iter,
                         train_data=train_data,
                         train_label=train_label,
                         save_conv_graph=save_conv_graph,
                         seed=seed)

        self.algo_name = 'AOA'
        self.agent_name = 'Agent'
        self.trans_function = None
        self.algo_params = {}

    def user_input(self):
        # initializing parameters
        self.algo_params['Min'] = float(input('Minimum value of the accelerated function [0-1]: ') or 0.1)
        self.algo_params['Max'] = float(input('Maximum value of the accelerated function [0-1]: ') or 0.9)
        self.algo_params['EPS'] = float(input('Value of epsilon [default: 1e-6]: ') or 1e-6)
        self.algo_params['alpha'] = float(input('Exploitation accuracy parameter [1-10]:' ) or 5)
        self.algo_params['mu'] = float(input('Control parameter to adjust the search process [0-1]:' ) or 0.5)

        # initializing transfer function
        self.algo_params['trans_function'] = input('Shape of Transfer Function [s/v/u] (default=s): ').lower() or 's'
        self.trans_function = get_trans_function(self.algo_params['trans_function'])

    def moa(self, Min, Max):
        return Min + (Max - Min) * self.cur_iter / self.max_iter

    def mop(self, alpha=5):
        return 1 - math.pow((self.cur_iter/self.max_iter), (1 / alpha))

    def exploration(self, i, j, MoP):
        # Eq. (3)
        r2 = np.random.random()
        if r2 >= 0.5:
            self.population[i][j] = self.Leader_agent[j] * (MoP + self.algo_params['EPS']) * self.algo_params['mu']
        else:
            self.population[i][j] = self.Leader_agent[j] / (MoP + self.algo_params['EPS']) * self.algo_params['mu']

    def exploitation(self, i, j, MoP):
        # Eq. (5)
        r3 = np.random.random()
        if r3 >= 0.5:
            self.population[i][j] = self.Leader_agent[j] + MoP * self.algo_params['mu']
        else:
            self.population[i][j] = self.Leader_agent[j] - MoP * self.algo_params['mu']

    def transfer_to_binary(self, i, j):
        if np.random.random() < self.trans_function(self.population[i][j]):
            self.population[i][j] = 1
        else:
            self.population[i][j] = 0

    def next(self):
        print('\n================================================================================')
        print('                          Iteration - {}'.format(self.cur_iter + 1))
        print('================================================================================\n')

        # Eq. (2)
        MoA = self.moa(self.algo_params['Min'], self.algo_params['Max'])

        # Eq. (4)
        MoP = self.mop(self.algo_params['alpha'])

        for i in range(self.num_agents):
            for j in range(self.num_features):

                r1 = np.random.random()
                if r1 > MoA:
                    self.exploration(i, j, MoP)  # Exploration phase (M,D)
                else:
                    self.exploitation(i, j, MoP)  # Exploitation phase (A,S)

                # convert to binary using transfer function
                self.transfer_to_binary(i, j)

        # increment current iteration
        self.cur_iter += 1


if __name__ == '__main__':
    data = datasets.load_digits()
    algo = AOA(num_agents=20,
               max_iter=100,
               train_data=data.data,
               train_label=data.target)

    solution = algo.run()
