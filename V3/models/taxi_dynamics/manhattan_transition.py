# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 21:31:21 2021

@author: Sarah Li
"""
import models.taxi_dynamics.manhattan_neighbors as manhattan
import numpy as np

def random_demand_generation(T, S):
    P_pick_up = np.zeros((T,S, S))
    demand_rate = []
    for s in range(S):
        demand_rate.append(np.random.randint(1e1, 5e2))
        for t in range(T):
            destinations = np.random.rand(S)
            P_pick_up[t, :, s] = destinations / np.sum(destinations)
        
    return P_pick_up, demand_rate


def uniform_initial_distribution(M):
    """ Return a uniform density array of drivers in Manhattan states. """
    state_num = len(manhattan.STATE_NEIGHBORS)
    p0 = np.ones(state_num) * M / state_num
    return p0


def transition_kernel(T, epsilon):
    """ Return a  4 dimensional transition kernel for Manhattan's MDP dynamics.
    
    Args: 
        T: total number of time steps within the MDP
        epsilon: the probability of not getting to neighbor state
    Returns:
        P: [T] x [S] x [S] x [A] transition kernel as ndarray.
        P_{ts'sa} is the probability of transitioning to s' from (s,a) at t.
    """
    S = len(manhattan.STATE_NEIGHBORS)
    A = manhattan.most_neighbors(manhattan.STATE_NEIGHBORS)
    # true action is A + 1: last action is reserved for picking up passengers.
    P_t = np.zeros((S, S, A + 1))  # kernel per time step. 
    
    for state, neighbors in manhattan.STATE_NEIGHBORS.items():
        N_n = len(neighbors) # number of neighbors
        # probability of arriving at correct neighbor
        p_target = 1 - N_n / (N_n -1) * epsilon
        # probability of arriving at another neighbor
        p_other_neighbor = epsilon/(N_n - 1) 
        
        action_ind = -1
        while action_ind < A:
            action_ind += 1
            neighbor = neighbors[-1]
            if action_ind < N_n:
                neighbor = neighbors[action_ind]
            # action goes to correct neighbor
            P_t[neighbor, state, action_ind] = p_target
            # action may take player to other neighbors
            for other_n in neighbors:
                P_t[other_n, state, action_ind] += p_other_neighbor
                
    P = np.zeros((T, S, S, A + 1))
    for t in range(T):
        P[t, :, :, :] = P_t
    return P
            
def test_transition_kernel(P):
    (T, S, _, A) = P.shape
    for t in range(T):
        for a in range(A-1):
            M = P[t, :, :, a]
            for s in range(S):
                col_sum = np.sum(M[:,s])
                # column stochasticity
                np.testing.assert_approx_equal(col_sum, 1, 4)