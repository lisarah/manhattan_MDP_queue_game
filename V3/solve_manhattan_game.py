# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 13:07:53 2021

@author: Sarah Li
"""
import numpy as np
# import gameSolvers.cvx as cvx
import algorithm.FW as fw
import models.mdpcg as mdpcg
import models.taxi_dynamics.manhattan_transition as m_dynamics
import models.taxi_dynamics.visualization as visual
import util.plot_lib as pt
import matplotlib.pyplot as plt
import matplotlib as mpl
import models.taxi_dynamics.manhattan_neighbors as m_neighbors

T = 15
epsilon = 1e-1
borough = 'Manhattan'
constrained_value = 250
manhattan_game = mdpcg.quad_game(T, manhattan=True)
initial_distribution = m_dynamics.uniform_initial_distribution(10000)
#----- CVX version ------ currently isn't running
# manhattan_game.solve(driver_distribution, verbose=True, returnDual=False)



x0 = np.zeros((manhattan_game.States, manhattan_game.Actions,
               manhattan_game.Time));   
y_opt, y_history = fw.FW(x0, initial_distribution, manhattan_game.P, 
                         manhattan_game.evaluate_cost, False, epsilon, 
                         maxIterations = 5000)
obj_history = [];
for i in range(len(y_history)):
	obj_history.append(manhattan_game.evaluate_objective(y_history[i]))

print(f'Last objective value is {obj_history[-1]}')

avg_cost = manhattan_game.evaluate_cost(y_opt)
print(f'Average driver reward is {np.sum(avg_cost)}')
#-----------visualize optimal distribution ------------------#
visual.plot_borough_progress(borough, y_opt, [0, int(T/2), T-1])

pt.objective(obj_history, None, 'Frank Wolfe')

constraint_violation= {}
density_dict = {}
min_density = 999
max_density = -1
state_ind = m_neighbors.zone_to_state(m_neighbors.zone_neighbors)
zone_ind = {y:x for x, y in state_ind.items()}
for s in range(manhattan_game.States):
    threshold = [np.sum(y_opt[s, :, t]) - constrained_value for t in range(T)]
        
    violations = [v for v in threshold if v > 0]
    violation =  sum([v for v in threshold if v > 0]) / T
    if violation > 0:
        constraint_violation[zone_ind[s]] = violation
    
    density_dict[zone_ind[s]] = np.sum([y_opt[s, :, t] for t in range(T)])/T
    min_density = min(list(density_dict.values()) + [min_density])
    max_density = max(list(density_dict.values()) + [max_density])

violation_density = {}
for z in constraint_violation.keys():  
    time_density = []
    for t in range(T):
        time_density.append(np.sum(y_opt[state_ind[z], :, t]))
    violation_density[z] = time_density

norm = mpl.colors.Normalize(vmin=(min_density), vmax=(max_density))
color_map = plt.get_cmap('coolwarm')
bar_colors = []
for violation in constraint_violation.values():
    R,G,B,A = color_map(norm(violation + constrained_value))
    bar_colors.append([R,G,B])   
bar_labels = ['West Village', 'World Trade Center', 'Yorkville West']  
  
fig_width = 5.3 * 2
f = plt.figure(figsize=(fig_width,8))
ax_bar = f.add_subplot(2,2,2)
bar_range = np.arange(1, len(constraint_violation) + 1, 1)
seq = [0,2,  1]
violations = []
for v in constraint_violation.values(): 
    violations.append(v)
loc_ind = 0
for bar_ind in seq:
    plt.bar(loc_ind, violations[bar_ind] + constrained_value, 
            width = 0.8, color=bar_colors[bar_ind], 
            label=bar_labels[bar_ind])
    loc_ind +=1
plt.ylim(250, 250 +1.1*max(constraint_violation.values()))
ax_bar.xaxis.set_visible(False)
plt.legend(fontsize=13)


f.add_subplot(2, 2, 4)
plt.plot(250*np.ones(T), linewidth = 6, alpha = 0.5, color=[0,0,0])
lines = []
for line in violation_density.values(): 
    lines.append(line)
for line_ind in seq:
    plt.plot(lines[line_ind], linewidth=3, 
             color=bar_colors[line_ind], label=bar_labels[line_ind])
plt.xlabel(r"Time",fontsize=13)
plt.grid()
plt.legend(fontsize=13)

ax = f.add_subplot(1, 2, 1)
visual.draw_borough(ax, density_dict, borough, 'average', color_map, norm)
ax.xaxis.set_visible(False)
ax.yaxis.set_visible(False)
plt.show()