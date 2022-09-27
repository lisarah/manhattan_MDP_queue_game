# manhattan_MDP_queue_game
This repository contains the python code for: 
1. A Markov decision process (MDP) model of Manhattan's ride-hail drivers. The model is built on the 2019 ride demand data from the [Taxi and Limosine Commission](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page).
	* Time: 12 or 15 minute intervals between 9 am and noon. 
	* States: states are consisted of \(z\), a Manhattan neighborhood zone, and \(q\), a queue level. A queue level of zero means the driver is in the given zone \(z\), a queue level greater than zero means that the driver is \(q \cdot \Delta t\) away from arriving in zone \(z\). 
	* Actions: actions are state dependent. At non-zero queue levels, the only action is to drop in queue. At the zeroth queue level, drivers can choose to wait for a rider or go to a neighboring zone. 
	* Transition: at higher queue levels, drivers stay in the same zone and drop in queue level with probability \(1\). At the zeroth queue level, if drivers choose to go to neighborhood zone, they transition to the target zone with configurable probability between \((0, 1)\). If drivers choose to pick up a rider, they transition to the rider's destination zone at the appropriate queue level. The probability distribution for riders' destination is determined by the 2019 ride demand data. 
	<p align="center">
	<img src="https://github.com/lisarah/manhattan_MDP_queue_game/blob/794ae3b38e682fc7413222cc4848625e4b7ade4c/queue_networks.png" width='300'/>
	</p>
	* Cost: cost of all transit actions have corresponding gas cost. Cost of all rider pick up actions are inversely proportional to the ride demand at each zone. 
2. A congestion game model built on top of the single driver MDP. For details, see [our paper](https://arxiv.org/abs/1907.08912).
1. A Frank-Wolfe gradient descent method that solves for the Wardrop equilibrium by iteratively performing value iteration.
2. An inexact gradient ascent method that enforces driver population constraints without explicit knowledge of game costs and dynamics.

The congestion game dynamics look like
<p align="center">
	<img src="https://github.com/lisarah/manhattan_MDP_queue_game/blob/6cd39b9f19cec06f60ba042b86b64a6d52192c2f/grad_res/toll_queue_game_unconstrained.gif" width="300" height="250"/>
</p>


To enforce driver population constraints, we use zone-based tolls. By tolling the most congested three zones, we are able to cap the driver population in those states to \(350\) drivers at any time. 
<p align="center">
	<img src="https://github.com/lisarah/manhattan_MDP_queue_game/blob/794ae3b38e682fc7413222cc4848625e4b7ade4c/grad_res/toll_queue_game_constrained.gif" width="300" height="250"/>
</p>


If you use our work, please cite! 
```
@article{li2019adaptive,
  title={Adaptive Constraint Satisfaction for Markov Decision Process Congestion Games: Application to Transportation Networks},
  author={Li, Sarah HQ and Yu, Yue and Miguel, Nicolas and Calderone, Dan and Ratliff, Lillian J and Acikmese, Behcet},
  journal={arXiv preprint arXiv:1907.08912},
  year={2019}
}
```

## Setting up the MDP model
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
