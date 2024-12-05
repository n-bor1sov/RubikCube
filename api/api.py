from flask import Flask, request, jsonify
import torch

import sys
sys.path.append('../')
sys.path.append('.')

from src.model import ValuePolicyNetwork
from src.solver import solve_cube
from src.env import *
import os

from flask_cors import CORS
app = Flask(__name__)
CORS(app)

# Initialize model and device globally
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = ValuePolicyNetwork()
model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'model.pth')
model.load_state_dict(torch.load(model_path, map_location=device))
model.to(device)
model.eval()

# Define the action set
action_set = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

@app.route('/solve', methods=['POST'])
def solve():
    # try:
    # Get data from request body
    data = request.get_json()
    
    # Convert lists to tensors
    moves = data['moves']
    cube = Cube()
    for move in moves:
        cube.move(move)
    corners, edges = cube.get_state()
    print(corners, edges)
    
    # Create initial state
    initial_state = (corners, edges)
    
    # Call solve_cube function
    _, solve_time, iterations, solved, solution = solve_cube(
        model=model,
        device=device,
        initial_state=initial_state,
        max_exploration=60000,
        action_set=action_set
    )
    print(solution, type(solution))
    print(solved, type(solved))
    print(solve_time, type(solve_time))
    print(iterations, type(iterations))
    print(solution[::-1])
    # Prepare response
    response = solution[::-1] if solved else None
    
    return jsonify(response)
    
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)
