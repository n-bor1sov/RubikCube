import torch

# Mapping moves to their respective indices
move2idx = {
    "U": 0,
    "Uc": 1,
    "F": 2,
    "Fc": 3,
    "L": 4,
    "Lc": 5,
    "R": 6,
    "Rc": 7,
    "B": 8,
    "Bc": 9,
    "D": 10,
    "Dc": 11
}

# Mapping indices to their respective moves
idx2move = {
    0: "U",
    1: "Uc",
    2: "F",
    3: "Fc",
    4: "L",
    5: "Lc",
    6: "R",
    7: "Rc",
    8: "B",
    9: "Bc",
    10: "D",
    11: "Dc"
}

# Corner position transformation matrices for each move
corner_moves = [
    [1, 3, 0, 2, 8, 9, 6, 7, 16, 17, 10, 11, 12, 13, 14, 15, 20, 21, 18, 19, 4, 5, 22, 23], # U
    [2, 0, 3, 1, 20, 21, 6, 7, 4, 5, 10, 11, 12, 13, 14, 15, 8, 9, 18, 19, 16, 17, 22, 23], # Uc
    [0, 1, 4, 6, 13, 5, 12, 7, 9, 11, 8, 10, 17, 19, 14, 15, 16, 3, 18, 2, 20, 21, 22, 23], # F
    [0, 1, 19, 17, 2, 5, 3, 7, 10, 8, 11, 9, 6, 4, 14, 15, 16, 12, 18, 13, 20, 21, 22, 23], # Fc
    [8, 1, 10, 3, 4, 5, 6, 7, 12, 9, 14, 11, 23, 13, 21, 15, 17, 19, 16, 18, 20, 2, 22, 0], # L
    [23, 1, 21, 3, 4, 5, 6, 7, 0, 9, 2, 11, 8, 13, 10, 15, 18, 16, 19, 17, 20, 14, 22, 12], # Lc
    [0, 22, 2, 20, 5, 7, 4, 6, 8, 1, 10, 3, 12, 9, 14, 11, 16, 17, 18, 19, 15, 21, 13, 23], # R
    [0, 9, 2, 11, 6, 4, 7, 5, 8, 13, 10, 15, 12, 22, 14, 20, 16, 17, 18, 19, 3, 21, 1, 23], # Rc
    [18, 16, 2, 3, 4, 0, 6, 1, 8, 9, 10, 11, 12, 13, 7, 5, 14, 17, 15, 19, 21, 23, 20, 22], # B
    [5, 7, 2, 3, 4, 15, 6, 14, 8, 9, 10, 11, 12, 13, 16, 18, 1, 17, 0, 19, 22, 20, 23, 21], # Bc
    [0, 1, 2, 3, 4, 5, 22, 23, 8, 9, 6, 7, 13, 15, 12, 14, 16, 17, 10, 11, 20, 21, 18, 19], # D
    [0, 1, 2, 3, 4, 5, 10, 11, 8, 9, 18, 19, 14, 12, 15, 13, 16, 17, 22, 23, 20, 21, 6, 7] # Dc
]

# Edge position transformation matrices for each move
edge_moves = [
    [2, 0, 3, 1, 8, 5, 6, 7, 16, 9, 10, 11, 12, 13, 14, 15, 20, 17, 18, 19, 4, 21, 22, 23], # U
    [1, 3, 0, 2, 20, 5, 6, 7, 4, 9, 10, 11, 12, 13, 14, 15, 8, 17, 18, 19, 16, 21, 22, 23], # Uc
    [0, 1, 2, 5, 4, 12, 6, 7, 10, 8, 11, 9, 18, 13, 14, 15, 16, 17, 3, 19, 20, 21, 22, 23], # F
    [0, 1, 2, 18, 4, 3, 6, 7, 9, 11, 8, 10, 5, 13, 14, 15, 16, 17, 12, 19, 20, 21, 22, 23], # Fc
    [0, 9, 2, 3, 4, 5, 6, 7, 8, 13, 10, 11, 12, 22, 14, 15, 18, 16, 19, 17, 20, 21, 1, 23], # L
    [0, 22, 2, 3, 4, 5, 6, 7, 8, 1, 10, 11, 12, 9, 14, 15, 17, 19, 16, 18, 20, 21, 13, 23], # Lc
    [0, 1, 21, 3, 6, 4, 7, 5, 8, 9, 2, 11, 12, 13, 10, 15, 16, 17, 18, 19, 20, 14, 22, 23], # R
    [0, 1, 10, 3, 5, 7, 4, 6, 8, 9, 14, 11, 12, 13, 21, 15, 16, 17, 18, 19, 20, 2, 22, 23], # Rc
    [17, 1, 2, 3, 4, 5, 0, 7, 8, 9, 10, 11, 12, 13, 14, 6, 16, 15, 18, 19, 22, 20, 23, 21], # B
    [6, 1, 2, 3, 5, 4, 15, 7, 8, 9, 10, 11, 12, 13, 14, 17, 16, 0, 18, 19, 21, 23, 20, 22], # Bc
    [0, 1, 2, 3, 4, 5, 6, 23, 8, 9, 10, 7, 14, 12, 15, 13, 16, 17, 18, 11, 20, 21, 22, 19], # D
    [0, 1, 2, 3, 4, 5, 6, 11, 8, 9, 10, 19, 13, 15, 12, 14, 16, 17, 18, 23, 20, 21, 22, 7] # Dc
]


class Cube:
    """
    Class representing a Rubik's Cube state and operations.

    Attributes:
        solved_corners (torch.Tensor): The solved state for the corners.
        solved_edges (torch.Tensor): The solved state for the edges.
        corners (torch.Tensor): The current state of the corners.
        edges (torch.Tensor): The current state of the edges.
    """
    def __init__(self):
        # Define the solved state for corners
        self.solved_corners = torch.zeros(8, dtype=torch.long)
        self.solved_corners[:4] = torch.arange(4)
        self.solved_corners[4:] = torch.arange(12, 16)

        # Define the solved state for edges
        self.solved_edges = torch.zeros(12, dtype=torch.long)
        self.solved_edges[:4] = torch.arange(4)
        self.solved_edges[4:6] = torch.arange(9, 11)
        self.solved_edges[6:8] = torch.arange(21, 23)
        self.solved_edges[8:] = torch.arange(12, 16)

        # Clone the solved state into current state
        self.corners = self.solved_corners.clone()
        self.edges = self.solved_edges.clone()

    def move(self, move_index: int):
        """
        Applies a move to the cube based on the given move index.

        Args:
            move_index (int): Index of the move to apply.
        """

        # Make copies of the current state to avoid modifying in-place
        edges_copy = self.edges.clone()
        corners_copy = self.corners.clone()

        # Apply the transformation for corners
        for i in range(8):
            self.corners[i] = corner_moves[move_index][corners_copy[i]]

        # Apply the transformation for edges
        for i in range(12):
            self.edges[i] = edge_moves[move_index][edges_copy[i]]

    def get_state(self):
        """
        Retrieves the current state of the cube.

        Returns:
            tuple: A tuple containing the corner and edge states as tensors.
        """
        return self.corners, self.edges

    def is_solved(self):
        """
        Checks if the cube is in a solved state.

        Returns:
            bool: True if the cube is solved, False otherwise.
        """
        return torch.all(self.corners == self.solved_corners) and torch.all(self.edges == self.solved_edges)

    def __str__(self):
        """
        Generates a string representation of the cube for visualization.

        Returns:
            str: A formatted string representing the cube's current state.
        """
        def fmt(value):
            # Formats a value position for printing.
            return f"{value:2}" if value != "*" else " *"

        # Map corners and edges to their positions
        corner_map = ["*"] * 24
        edge_map = ["*"] * 24

        for i, pos in enumerate(self.corners):
            corner_map[pos.item()] = i

        for i, pos in enumerate(self.edges):
            edge_map[pos.item()] = i
        # Create the layout
        layout = [
            "          ┌──┬──┬──┐",
            f"          │{fmt(corner_map[0])}│{fmt(edge_map[0])}│{fmt(corner_map[1])}│",
            "          ├──┼──┼──┤",
            f"          │{fmt(edge_map[1])}│ *│{fmt(edge_map[2])}│",
            "          ├──┼──┼──┤",
            f"          │{fmt(corner_map[2])}│{fmt(edge_map[3])}│{fmt(corner_map[3])}│",
            " ┌──┬──┬──┼──┼──┼──┼──┬──┬──┬──┬──┬──┐",
            f" │{fmt(corner_map[16])}│{fmt(edge_map[16])}│{fmt(corner_map[17])}│{fmt(corner_map[8])}│{fmt(edge_map[8])}│{fmt(corner_map[9])}│{fmt(corner_map[4])}│{fmt(edge_map[4])}│{fmt(corner_map[5])}│{fmt(corner_map[20])}│{fmt(edge_map[20])}│{fmt(corner_map[21])}│",
            " ├──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┤",
            f" │{fmt(edge_map[17])}│ *│{fmt(edge_map[18])}│{fmt(edge_map[9])}│ *│{fmt(edge_map[10])}│{fmt(edge_map[5])}│ *│{fmt(edge_map[6])}│{fmt(edge_map[21])}│ *│{fmt(edge_map[22])}│",
            " ├──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┤",
            f" │{fmt(corner_map[18])}│{fmt(edge_map[19])}│{fmt(corner_map[19])}│{fmt(corner_map[10])}│{fmt(edge_map[11])}│{fmt(corner_map[11])}│{fmt(corner_map[6])}│{fmt(edge_map[7])}│{fmt(corner_map[7])}│{fmt(corner_map[22])}│{fmt(edge_map[23])}│{fmt(corner_map[23])}│",
            " └──┴──┴──┼──┼──┼──┼──┴──┴──┴──┴──┴──┘",
            f"          │{fmt(corner_map[12])}│{fmt(edge_map[12])}│{fmt(corner_map[13])}│",
            "          ├──┼──┼──┤",
            f"          │{fmt(edge_map[13])}│ *│{fmt(edge_map[14])}│",
            "          ├──┼──┼──┤",
            f"          │{fmt(corner_map[14])}│{fmt(edge_map[15])}│{fmt(corner_map[15])}│",
            "          └──┴──┴──┘"
        ]

        s = ""
        for line in layout:
            s += line
            s += "\n"
        return s
