# app/ml/fl_client.py

import argparse
from typing import Dict, List

import numpy as np
import requests
import torch
import torch.nn as nn
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.models import Student, User
from app.ml.model import PFLRecommender, get_shared_state, set_shared_state
from app.ml.features import get_input_dim, get_student_feedback_dataset


API_BASE = "http://127.0.0.1:8000/api/v1/fl"
# In a real deployment, API_BASE would be the URL of the central aggregator.


def build_client_dataset(db: Session, client_id: str):
    """
    Collect (X, y) for ALL students that belong to this client_id.

    Here we assume:
    - User table has a 'client_id' field indicating which organization they belong to.
    """
    X_list = []
    y_list = []

    students = (
        db.query(Student)
        .join(User, User.id == Student.user_id)
        .filter(User.client_id == client_id)
        .all()
    )

    for s in students:
        X_s, y_s = get_student_feedback_dataset(db, s)
        if X_s.shape[0] == 0:
            continue
        X_list.append(X_s)
        y_list.append(y_s)

    if not X_list:
        return np.empty((0, 1), dtype=np.float32), np.empty((0,), dtype=np.float32)

    X = np.concatenate(X_list, axis=0).astype(np.float32)
    y = np.concatenate(y_list, axis=0).astype(np.float32)
    return X, y


def train_local_client(client_id: str, admin_token: str, epochs: int = 3):
    """
    This is the LOCAL FL CLIENT procedure:

    1. Get global shared weights from aggregator.
    2. Build local dataset from *local DB* (no data leaves this node).
    3. Train locally.
    4. Send updated shared weights back to aggregator.
    """
    db = SessionLocal()
    try:
        X, y = build_client_dataset(db, client_id)
        if X.shape[0] == 0:
            print(f"[{client_id}] No local data to train on.")
            return

        input_dim = get_input_dim()

        # 1. Download global shared state from aggregator
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = requests.get(f"{API_BASE}/global-model", headers=headers)
        resp.raise_for_status()
        payload = resp.json()
        shared_json = payload["shared_state"]

        shared_state = {k: torch.tensor(v, dtype=torch.float32) for k, v in shared_json.items()}

        # 2. Local model
        model = PFLRecommender(input_dim)
        set_shared_state(model, shared_state)

        X_tensor = torch.from_numpy(X)
        y_tensor = torch.from_numpy(y)

        loss_fn = nn.BCELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

        model.train()
        for _ in range(epochs):
            optimizer.zero_grad()
            preds = model(X_tensor).squeeze()
            loss = loss_fn(preds, y_tensor)
            loss.backward()
            optimizer.step()

        # 3. Extract updated shared weights and send back to aggregator
        updated_shared = get_shared_state(model)
        json_state = {k: v.detach().cpu().numpy().tolist() for k, v in updated_shared.items()}

        update_payload = {
            "client_id": client_id,
            "shared_state": json_state,
        }

        resp2 = requests.post(f"{API_BASE}/submit-update", json=update_payload, headers=headers)
        resp2.raise_for_status()
        print(f"[{client_id}] Local training done and update sent to aggregator.")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-id", required=True, help="Logical client ID (e.g. university code)")
    parser.add_argument("--admin-token", required=True, help="Admin JWT token for authent icating with aggregator")
    parser.add_argument("--epochs", type=int, default=3)
    args = parser.parse_args()

    train_local_client(args.client_id, args.admin_token, epochs=args.epochs)
