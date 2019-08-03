# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 14:50:12 2019

@author: craba
"""
import mdpcg as mrg
import util.mdp as mdp

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
Time = 20;

sGame = mrg.mdpcg(Time);
seattleGraph=sGame("G");
sGame.setQuad();
#nx.draw(seattleGraph, pos = sGame("graphPos"),with_labels=True);
#plt.show()
#p0 = np.ones((seattleGraph.number_of_nodes()))/seattleGraph.number_of_nodes();
p0 = np.zeros((seattleGraph.number_of_nodes()));
#p0[0] = 1.0;
# make all drivers start from residential areas 6 of them
residentialNum = 0.1;
p0[2] = 1./residentialNum;
p0[3] = 1./residentialNum;
p0[7] = 1./residentialNum;
p0[8] = 1./residentialNum;
p0[10] = 1./residentialNum;
p0[11] = 1./residentialNum;

print ("Solving primal unconstrained case");
optRes, mdpRes = sGame.solve(p0, verbose=False,returnDual=False);