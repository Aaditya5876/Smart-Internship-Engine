import os
from typing import Dict

import torch
import torch.nn as nn

MODEL_DIR = "models"
GLOBAL_MODEL_PATH = os.path.join(MODEL_DIR, "global_pfl_model.pt")


class PFLRecommender(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.shared = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
        )
        self.personal = nn.Sequential(
            nn.Linear(64, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid(),
        )
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.shared(x)
        return self.personal(x)


def init_global_model(input_dim: int) -> PFLRecommender:
    model = PFLRecommender(input_dim)
    return model


def save_global_model(model: PFLRecommender):
    os.makedirs(MODEL_DIR, exist_ok=True)
    torch.save(model.state_dict(), GLOBAL_MODEL_PATH)


def load_global_model(input_dim: int) -> PFLRecommender:
    model = PFLRecommender(input_dim)
    if os.path.exists(GLOBAL_MODEL_PATH):
        state = torch.load(GLOBAL_MODEL_PATH, map_location="cpu")
        model.load_state_dict(state)
    return model


def get_shared_state(model: PFLRecommender) -> Dict[str, torch.Tensor]:
    return {k: v for k, v in model.state_dict().items() if k.startswith("shared.")}


def set_shared_state(model: PFLRecommender, shared_state: Dict[str, torch.Tensor]):
    current = model.state_dict()
    for k, v in shared_state.items():
        current[k] = v
    model.load_state_dict(current)
