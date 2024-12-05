# RubikCube

## Requirements

- numpy
- torch
- tqdm

## Overview

This project implements a Rubik's Cube solver using deep reinforcement learning. It combines a value-policy neural network with Monte Carlo Tree Search (MCTS) to find solutions for scrambled Rubik's Cubes.

## Features

- Deep neural network that learns both value and policy functions
- Monte Carlo Tree Search implementation for cube solving
- Flask API server for solving cubes via HTTP requests

## Usage
  
  pip install -r requirements.txt
  
  python api/api.py
  
  cd front/rubiks-cube
  
  npm install
  
  npm run dev
