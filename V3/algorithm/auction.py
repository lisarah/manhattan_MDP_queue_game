# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 17:33:50 2021

Created the auction algorithm to solve a min flow problem.
https://en.wikipedia.org/wiki/Auction_algorithm

min \sum_{s} \sum_{a}C_{sa}y_{sa}
s.t.\sum_{a} y_{sa} = 1, \forall s \in [S] 
    \sum_{s} y_{sa} = 1, \forall a \in [A]
    y_{sa} \geq 0, \forall (s,a) \in [S] \times [A]

@author: Sarah Li
"""

def auction(flow_problem, initial_prices, epsilon = 0.01, verbose = False):
    """ The auction algorithm for solving minimum flow problem. 
    
    Args:
        flow_problem: containing states, actions and cost.
        initial_prices: a guess of initial prices, list length must the number
        of actions in flow_problem.
        
    Returns:
        optimal_bidder: a dictionary of optimal bidders (value) for each 
        action (key).
    """
    state_num = len(flow_problem.states)
    action_num = len(flow_problem.actions)
    optimal_bidders = {}
    prices = initial_prices
    # initialize bidder dictionary.
    for a_ind in range(action_num):
        optimal_bidders[a_ind] = None
        
    unassigned_bidders = [x for x in range(state_num)] # everyone is unassigned
    # print (unassigned_bidders)
    max_iter = 100
    iteration = 0
    while len(unassigned_bidders) > 0 and iteration < max_iter:
        iteration += 1
        bids = {}
        for a_ind in range(action_num):
            bids[a_ind] = {}
            
        # states decide who to bid 
        for s_ind in unassigned_bidders:
            deltas = []
            for a_ind in range(action_num):
                deltas.append(prices[a_ind] - flow_problem.cost[s_ind][a_ind])
            best_delta = max(deltas)
            best_delta_ind = deltas.index(best_delta)
            deltas.pop(best_delta_ind)
            second_best_delta = max(deltas)
            delta_delta = best_delta - second_best_delta
            bid_price = prices[best_delta_ind] - delta_delta - epsilon
            bids[best_delta_ind][bid_price] = s_ind
        
        # actions delegated to the lowest bidder
        for a_ind in range(action_num):
            new_bids = bids[a_ind].keys()
            if new_bids:
                lowest_bid = min(new_bids)
                winner_ind = bids[a_ind][lowest_bid]
                prices[a_ind] = lowest_bid
                if optimal_bidders[a_ind] != winner_ind:
                    if optimal_bidders[a_ind] is not None:
                        unassigned_bidders.append(optimal_bidders[a_ind])
                    unassigned_bidders.remove(winner_ind)
                    optimal_bidders[a_ind] = winner_ind
                if verbose:
                    print (f'action {a_ind} has new bidder {winner_ind}')
                
    if iteration >= max_iteration:
        print('warning: max iteration reached in auction algorithm.')
    return optimal_bidders 
            