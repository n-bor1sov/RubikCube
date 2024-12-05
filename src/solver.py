import numpy as np
from src.tree import MCTS
from src.env import *
from src.model import ValuePolicyNetwork, hash_state

import torch
import torch.nn.functional as F
import time
import random

def calculate_val(state, action_set, model, device):
    if state.val is None and state.P is None:
        # Get predictions from model
        cube_representation = torch.concat([state.corners, state.edges], dim=0)
        # print(cube_representation)
        cube_representation_encoded = F.one_hot(cube_representation, num_classes=24).float().to(device)
        with torch.no_grad():
            val, policy = model(cube_representation_encoded.unsqueeze(0))
        policy = F.softmax(policy[0], dim=0).numpy()
        state.P = policy
        state.val = float(val[0][0])
        state.W = state.val * np.ones(len(action_set))
        
    return state

def print_tree_levels(root_node, max_depth=3):
    """
    Prints the number of children at each level of the tree.
    
    Args:
        root_node: The root node of the MCTS tree
        max_depth: Maximum depth to explore (default: 3)
    """
    current_level = [root_node]
    depth = 0
    
    while current_level and depth < max_depth:
        # Count children for each node at current level
        children_counts = []
        next_level = []
        
        for node in current_level:
            # Count number of children
            n_children = len(node.ActToChildren)
            children_counts.append(n_children)
            
            # Collect all children for next level
            next_level.extend(node.ActToChildren.values())
        
        # Print information for current level
        print(f"Depth {depth}: {len(current_level)} nodes with children counts: {children_counts}")
        
        # Move to next level
        current_level = next_level
        depth += 1

def solve_cube(model, device, initial_state, max_exploration=50, action_set=None):
    """
    Attempts to solve a Rubik's cube from a given initial state using MCTS
    
    Args:
        model: The nn model that defines the policy
        device: torch.device()
        initial_state: The initial cube state (labels)
        max_exploration: Maximum number of exploration steps (default: 50)
        action_set: List of possible moves (if None, uses default moves)
    
    Returns:
        tuple: (solution, solve_time, iterations)
            - solution: List of moves to solve the cube, or None if unsolved
            - solve_time: Time taken to find solution
            - iterations: Number of iterations needed
    """
    
    t = time.time()
    i = 1
    
    tree = MCTS(initial_state)
    solved, solution_node = False, None
    solution_actions = []
    current_node = tree.getRoot()
    while i < max_exploration:
        if not current_node.isLeaf():
            A = current_node.Q() + current_node.U()
            a = action_set[np.argmax(A)]
            current_node.state.loss_update(a)
            current_node = current_node.get_child(a)
            
        else:
            # Extend
            corners, edges = current_node.getState()
            for a in action_set:
                cube = Cube(torch.tensor(corners.clone()), torch.tensor(edges.clone()))
                cube.move(a)
                next_state = cube.get_state()
                solved = cube.is_solved()
                new_node = tree.add(next_state, current_node, a)
                if solved:
                    solution_node = new_node
                    break
            if not solved:
                # Backpropagation
                current_node.state = calculate_val(current_node.state, action_set, model, device)
                A = current_node.Q() + current_node.U()
                a = action_set[np.argmax(A)]
                current_node.state.loss_update(a)

                # print(a, current_node.state.val)
                current_node.update(a, current_node.state.val)
                parent, a = current_node.get_parent()
                while parent:
                    parent.update(a, current_node.state.val)
                    current_node = parent
                    parent, a = current_node.get_parent()

                # Start over
                current_node = tree.getRoot()
                i += 1

        if solved:
            while solution_node.state is not tree.getRoot().state:
                parent, a = solution_node.get_parent()
                solution_actions.append(a)
                solution_node = parent
            solution_actions.reverse()
            print(f"Solution: {solution_actions}")
            break
    
    solve_time = time.time() - t
    
    return None, solve_time, i, solved, solution_actions
