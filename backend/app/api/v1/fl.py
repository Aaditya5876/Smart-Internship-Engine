# app/api/v1/fl.py

from typing import Dict, List

import torch
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.ml.model import load_global_model, save_global_model, get_shared_state, set_shared_state
from app.ml.features import get_input_dim
from app.ml.pfl_train import fed_avg
from app.services.deps import require_admin  # or a special "aggregator" auth if you want

router = APIRouter(prefix="/fl", tags=["federated"])

# In-memory storage of pending client updates for the current round
PENDING_UPDATES: List[Dict[str, List[float]]] = []


class FLUpdate(BaseModel):
    client_id: str
    shared_state: Dict[str, List[float]]  # param_name -> flat list of floats


@router.get("/global-model", dependencies=[Depends(require_admin)])
def get_global_model():
    """
    Aggregator endpoint:
    Return the current global SHARED model weights only.
    No database access, only model file.
    """
    input_dim = get_input_dim()
    model = load_global_model(input_dim)
    shared_state = get_shared_state(model)

    # Convert tensors to plain Python lists for JSON
    json_state = {k: v.detach().cpu().numpy().tolist() for k, v in shared_state.items()}
    return {"shared_state": json_state}


@router.post("/submit-update", dependencies=[Depends(require_admin)])
def submit_update(update: FLUpdate):
    """
    Aggregator endpoint:
    Receive one client's updated shared weights.
    Again: no DB access, only in-memory + model file.
    """
    PENDING_UPDATES.append(update.shared_state)
    return {"detail": f"Update received from client {update.client_id}", "pending": len(PENDING_UPDATES)}


@router.post("/aggregate", dependencies=[Depends(require_admin)])
def aggregate():
    """
    Aggregator endpoint:
    Aggregate all pending updates via FedAvg and update the global model.
    """
    if not PENDING_UPDATES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending client updates to aggregate.",
        )

    input_dim = get_input_dim()
    model = load_global_model(input_dim)

    # Convert JSON shared_states (lists) -> torch tensors
    state_dicts = []
    for json_state in PENDING_UPDATES:
        sd = {}
        for k, v in json_state.items():
            sd[k] = torch.tensor(v, dtype=torch.float32)
        state_dicts.append(sd)

    new_shared = fed_avg(state_dicts)
    set_shared_state(model, new_shared)
    save_global_model(model)

    PENDING_UPDATES.clear()
    return {"detail": "Global model updated via FedAvg", "num_clients": len(state_dicts)}
