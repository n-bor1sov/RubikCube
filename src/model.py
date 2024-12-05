import torch
import torch.nn as nn
from src.env import *
import torch.nn.functional as F
from torch.nn.init import xavier_uniform_

class ValuePolicyNetwork(nn.Module):
    def __init__(self):
        super(ValuePolicyNetwork, self).__init__()

        # Define shared layers
        self.shared_layers = nn.Sequential(
            nn.Linear(480, 4096),
            nn.LayerNorm(4096),
            nn.ELU(),
            nn.Linear(4096, 2048),
            nn.LayerNorm(2048),
            nn.ELU()
        )

        # Define value head
        self.value_head = nn.Sequential(
            nn.Linear(2048, 512),  # 2048 -> 512
            nn.LayerNorm(512),
            nn.ELU(),
            nn.Linear(512, 1)  # 512 -> 1 (scalar value)
        )

        # Define policy head
        self.policy_head = nn.Sequential(
            nn.Linear(2048, 512),  # 2048 -> 512
            nn.LayerNorm(512),
            nn.ELU(),
            nn.Linear(512, 12)  # 512 -> 12 (policy logits)
        )
        
        # Apply Glorot initialization
        self.apply(self._init_weights)

    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            xavier_uniform_(m.weight)  # Glorot initialization for weights
            if m.bias is not None:
                nn.init.zeros_(m.bias)

    def forward(self, x):
        # Transform input
        b = x.shape[0]
        x = x.view(b, -1)
        shared_out = self.shared_layers(x)
        value_out = self.value_head(shared_out)
        policy_out = self.policy_head(shared_out)
        return value_out, policy_out

def hash_state(corners, edges):
    return f"{''.join(str(x) for x in corners.tolist())}{''.join(str(x) for x in edges.tolist())}"
