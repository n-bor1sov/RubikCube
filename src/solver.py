import numpy as np
from treelib import Tree
import sys

sys.path.append("../")
from src.tree import MCTS
from src.env import *
from src.model import ValuePolicyNetwork, hash_state

import torch
import torch.nn.functional as F
import time
import random
# from tqdm import tqdm
# import seaborn as sns
# import matplotlib.pyplot as plt

device = torch.device("cpu")
# Prepare model
model = ValuePolicyNetwork()
model.load_state_dict(torch.load("../models/model.pth", map_location=device , weights_only=False))
model.to(device)
model.eval()

solve_time = []

n_solves = []

def calculateVal(state, action_set):
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

def solve_cube(initial_state, max_exploration=50, action_set=None):
    """
    Attempts to solve a Rubik's cube from a given initial state using MCTS
    
    Args:
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
    solved, solved_state = False, None
    
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
            cube = Cube(torch.tensor(corners), torch.tensor(edges))
            for a in action_set:
                cube.move(a)
                next_state = cube.get_state()
                solved = cube.is_solved()
                new_node = tree.add(next_state, current_node, a)
                if solved:
                    solver = new_node
                    break
            
            # Backpropagation
            current_node.state = calculateVal(current_node.state, action_set)

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
                
            # New start
            current_node = tree.getRoot()
            i += 1
        
        if solved:
            break
    
    solve_time = time.time() - t
    print(solved)
    print_tree_levels(tree.getRoot())
    # if solved:
    #     solution = []
    #     _, min_solver = tree.BFS(solver.state)
    #     parent, a = min_solver.get_parent()
    #     while parent:
    #         solution = [a] + solution
    #         parent, a = parent.get_parent()
    #     return solution, solve_time, i
    
    return None, solve_time, i, solved

# Test solving multiple scrambled cubes
num_cubes = 10
scramble_length = 4
solved_count = 0

total_time = 0
total_iterations = 0

print(f"\nTesting solver on {num_cubes} cubes scrambled with {scramble_length} moves each...")

for cube_num in range(num_cubes):
    cube = Cube()
    scramble_moves = []
    
    # Scramble the cube
    for _ in range(scramble_length):
        move = random.randint(0, 11)
        scramble_moves.append(move)
        cube.move(move)
        
    print(f"\nCube {cube_num + 1}")
    print(f"Scramble sequence: {scramble_moves}")
    
    corners, edges = cube.get_state()
    solution, solve_time, iterations, solved = solve_cube(
        initial_state=(corners, edges),
        max_exploration=20000,
        action_set=list(range(12))
    )
    
    if solved:
        solved_count += 1
        
    total_time += solve_time
    total_iterations += iterations
    
    print(f"Solution found: {solved}")
    print(f"Solve time: {solve_time:.2f}s")
    print(f"Iterations: {iterations}")

success_rate = (solved_count / num_cubes) * 100
avg_time = total_time / num_cubes
avg_iterations = total_iterations / num_cubes

print(f"\nResults:")
print(f"Success rate: {success_rate:.1f}%")
print(f"Average solve time: {avg_time:.2f}s")
print(f"Average iterations: {avg_iterations:.1f}")