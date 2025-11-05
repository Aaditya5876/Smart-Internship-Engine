
import torch
import torch.nn as nn
from pathlib import Path
import pickle
import numpy as np
from typing import List, Dict
from app.core.config import get_settings

# settings = get_settings()
settings = get_settings

class Backbone(nn.Module):
    def __init__(self, input_dim=9, hidden=64):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(input_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU()
        )
    def forward(self,x):
        return self.mlp(x)

class Head(nn.Module):
    def __init__(self, hidden=64):
        super().__init__()
        self.out = nn.Linear(hidden,1)
    def forward(self,h):
        return self.out(h)

class PFLRegistry:
    def __init__(self):
        self.backbone_path = Path(settings.BACKBONE_PATH)
        self.heads_dir = Path(settings.HEADS_DIR)
        self.preproc_path = Path(settings.PREPROCESSOR_PATH)

        # load preprocessor
        with open(self.preproc_path,"rb") as f:
            self.preproc = pickle.load(f)

        # load backbone
        self.backbone = Backbone()
        if self.backbone_path.exists():
            self.backbone.load_state_dict(torch.load(self.backbone_path, map_location="cpu"))
        self.backbone.eval()

    def _load_head(self, client_id: str) -> Head:
        head = Head()
        hpath = self.heads_dir / f"{client_id}.pt"
        if hpath.exists():
            head.load_state_dict(torch.load(hpath, map_location="cpu"))
        head.eval()
        return head

    def predict(self, client_id: str, X: np.ndarray) -> np.ndarray:
        Xs = self.preproc.transform(X)
        xt = torch.tensor(Xs, dtype=torch.float32)
        with torch.no_grad():
            h = self.backbone(xt)
            head = self._load_head(client_id)
            y = head(h).squeeze(-1).numpy()
        return y
