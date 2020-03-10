#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 09:45:40 2020

@author: sarahli
"""
import numpy  as np
import util.mdp as mdp
import gameSolvers.mdpcg as conGame
P, C, D, S, A = mdp.airportMDP()
    
    
p0 = np.zeros((S));
p0[:6] = np.random.rand((6));
p0 = p0/sum(p0)*20;
#print (p0);
Time = 10;    

gateAssign = conGame.game(P, S, A, C,D,Time);
optDistri, mdpRes = gateAssign.solve(p0)
    
    
    
    
    
    
    
    
    
    
    
    
    
    