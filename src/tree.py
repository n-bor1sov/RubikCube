# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
import numpy as np
from src.env import *
from queue import LifoQueue as Queue
from src.model import hash_state


import torch
import torch.nn.functional as F
device = torch.device("cpu")

mu = 1000
c = 40

n_a = len(move2idx.keys())

class State(object): 

	def __init__(self, state): 
		self.W = np.zeros(n_a) # Max value of action
		self.N = np.zeros(n_a) # Number of visits
		self.L = np.zeros(n_a) # Loss for action
		self.P, self.val = None,None # Policy and value
		self.corners = state[0]
		self.edges = state[1]
		self.state_hash = hash_state(state[0], state[1])
		self.totalN = 0 # Total number of visits
		self.depth = np.inf # Depth of the node
		self.min_depth_node = None

	def Q(self):
		return(self.W - self.L)

	def U(self):
		return(c * self.P * np.sqrt(self.totalN)/(1+self.N))

	def loss_update(self, action):
		self.L[action] += mu
	
	def update(self, action, val):
		self.W[action] = max(self.W[action], val)
		self.N[action] += 1
		self.L[action] -= mu
		self.totalN += 1
  
	def getVal(self):
		if self.val is None:
			# Get predictions from model
			cube_representation = torch.concat([self.corners, self.edges], dim=0)
			cube_representation_encoded = F.one_hot(cube_representation, num_classes=24).float().to(device)
			with torch.no_grad():
				val, policy = model(cube_representation_encoded.unsqueeze(0))
			
			self.P = F.softmax(policy[0], dim=0).numpy()
			self.val = val.item()
			self.W = self.val * np.ones(n_a)
			return self.val
		

	
class StateNode(object):
	def __init__(self, state, action = None, parent = None): # State state, NodeState parent
		
		self.state = state
		self.parent = parent
		self.ActFromParent = action # {StateNode n :action a}
		self.ActToChildren = dict() # {action a : StateNode n}
		self.depth = 0
		self.is_leaf = True
		
		if parent:
			self.depth = min(self.parent.Depth()+1, self.Depth())
		
		if self.depth < self.Depth():
			self.state.depth = self.depth
			self.state.min_depth_node = self
		

	def update(self, action, val):
		self.state.update(action, val)

	def W(self):
		return(self.state.W)

	def N(self):
		return(self.state.N)
		
	def L(self):
		return(self.state.L)

	def Q(self):
		return(self.state.Q())

	def U(self):
		return(self.state.U())
		
	def Depth(self):
		return(self.state.depth)

	def getState(self):
		return self.state.corners, self.state.edges
	
	def getStateHash(self):
		return(self.state.state_hash)

	def getVal(self):
		return(self.state.getVal())

	def add_children(self, node, action):
		self.ActToChildren[action] = node
		self.is_leaf = False
		
	def get_child(self,a):
		return(self.ActToChildren[a])
	
	def isLeaf(self):
		return(self.is_leaf)
	
	def get_parent(self):
		return(self.parent, self.ActFromParent)
	

class MCTS(object):
	def __init__(self, initial_state):

		self.root = StateNode(State(initial_state))
		self.visited_states = {self.root.getStateHash():self.root.state}

	def __contains__(self, stateId):
		return(stateId in self.visited_states)
	
	def getRoot(self):
		return(self.root)
		
	def add(self, state, parent, action):
		stateHash = hash_state(state[0], state[1])
		if stateHash not in self.visited_states:
			new_state = State(state)
			new_node = StateNode(new_state, action, parent)
			self.visited_states[stateHash] = new_state
		else:
			new_node = StateNode(self.visited_states[stateHash], action, parent)
		parent.add_children(new_node, action)
		return(new_node)
	
	def BFS(self,state):
		stateHash = hash_state(state.state_id)
		depths = {k : v.min_depth_node for k,v in self.visited_states.items()}
		change = True
		while change:
			change = False
			for k,node in depths.items():
				if node and node.parent and node.parent.Depth()+1 < node.Depth():
					node.state.depth = node.parent.Depth()+1
					change = False
		return(depths[stateHash].Depth(),depths[stateHash])
