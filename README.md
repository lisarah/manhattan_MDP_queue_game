# manhattan_MDP_queue_game
This repository contains python code for the Markov decision process (MDP) congestion games, a game model for large groups of users with Markov decision process dynamics. Two algorithms are developed for the game: 
1. A Frank-Wolfe gradient descent method that solves for the Wardrop equilibrium by iteratively performing value iteration.
2. An inexact gradient ascent method that enforces driver population constraints without explicit knowledge of game costs and dynamics.

The MDP congestion game is illustrated on a Uber driver set up with MDP dynamics in New York city generated from 1million Uber pick-up data from [Taxi and Limosine Commission](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page).

<img src="https://github.com/lisarah/manhattan_MDP_queue_game/grad_res/toll_queue_game_unconstrained.gif" width="40" height="40" />

For details of the MDP model, see [arxiv paper](https://arxiv.org/abs/1907.08912).

If you use our work, please cite! 
```
@article{li2019adaptive,
  title={Adaptive Constraint Satisfaction for Markov Decision Process Congestion Games: Application to Transportation Networks},
  author={Li, Sarah HQ and Yu, Yue and Miguel, Nicolas and Calderone, Dan and Ratliff, Lillian J and Acikmese, Behcet},
  journal={arXiv preprint arXiv:1907.08912},
  year={2019}
}
```

## Setting up the NYC example
1. Download trip data and the file `taxi+_zone_lookup.csv` from [TLC](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page) into a new folder taxi_data under models. Current example uses `yellow_tripdata_2019-01.csv` and `yellow_tripdata_2019-12.csv`. Also download taxi look
2. Double check that line `169` in `models/nyc_data_processing.py` is set to `True`, and run `nyc_data_processing.py`. This should generate `distance_matrix.csv` and processed trip pickles into `models/taxi_data`
3. Run `models/taxi_model_gen.py`
3. Run `solve_queued_game.py' for generating gif for the unconstrained equilibrium distribution.
3. Run `solve_tolled_queued_game.py' for generating gifs for the unconstrained and constrained equilibrium distribution.


<!-- ## Content
1. MDP dynamic models: 
	* A mock up MDP with 3 x 5 grid states. Each state has 4 actions: left/right/up/down, where each action takes the user to the target neighbouring state with probability 0 < p < 1 and to another neighbouring state with probability 1-p. 
	* Uber drivers' MDP dynamics in Seattle, WA. See [Tolling for Constraint Satisfaction in MDP Congestion Games](https://arxiv.org/pdf/1903.00747.pdf)  for more model details.
	* 
	* Wheatstone MDP dynamics (V2 only)- for demonstrating of Braess paradox in MDP congestion games. See [Sensitivity Analysis for MDP Congestion games](https://arxiv.org/pdf/1909.04167.pdf) for model description and Braess paradox description.
	* Airport gate assignment MDP dynamics. See [overleaf doc](https://www.overleaf.com/read/tnzgddzckbsh
) for description.
2. Game solvers
	* CVXPY 
	* Custom solver - Frank Wolfe + dynamic programming - with automatic step size generation. See [Tolling for Constraint Satisfaction in MDP Congestion Games](https://arxiv.org/pdf/1903.00747.pdf) for convergence guarantees.
3. Incentive solvers
	* Constrained CVXPY
	* Projected dual ascent
	* ADMM
	* Mystic - a nonconvex solver for non-convex constraints (experimental)
4. Data visualization - custom visualization methods for displaying Wardrop equilibrium and online solutions.
 -->
