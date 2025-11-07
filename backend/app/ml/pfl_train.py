# app/ml/pfl_train.py

import copy
from typing import List

import torch
import torch.nn as nn
import numpy as np
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.models import Student
from app.ml.model import (
    PFLRecommender,
    load_global_model,
    save_global_model,
    get_shared_state,
    set_shared_state,
)
from app.ml.features import get_student_feedback_dataset, get_input_dim


def train_local(
    student: Student,
    global_shared_state,
    db: Session,
    input_dim: int,
    epochs: int = 3,
) -> dict | None:
    """
    Local PFL training on one client's (student's) feedback.
    Returns updated shared state dict, or None if no data.
    """
    X, y = get_student_feedback_dataset(db, student)
    if X.shape[0] == 0:
        return None

    X_tensor = torch.from_numpy(X)
    y_tensor = torch.from_numpy(y)

    local_model = PFLRecommender(input_dim)
    set_shared_state(local_model, global_shared_state)

    loss_fn = nn.BCELoss()
    optimizer = torch.optim.Adam(local_model.parameters(), lr=1e-3)

    local_model.train()
    for _ in range(epochs):
        optimizer.zero_grad()
        preds = local_model(X_tensor).squeeze()
        loss = loss_fn(preds, y_tensor)
        loss.backward()
        optimizer.step()

    return get_shared_state(local_model)


def fed_avg(states: List[dict]) -> dict:
    """Classical FedAvg over shared layers."""
    avg_state = copy.deepcopy(states[0])
    for k in avg_state.keys():
        for s in states[1:]:
            avg_state[k] += s[k]
        avg_state[k] /= len(states)
    return avg_state


def run_federated_round(min_feedback: int = 3):
    """
    One PFL / FL round across all students with at least `min_feedback` samples.

    This is what you reference for RQ1 + RQ2:
    - data heterogeneity handled via client-specific training
    - privacy preserved as only model parameters are exchanged
    """
    db = SessionLocal()
    try:
        input_dim = get_input_dim()

        global_model = load_global_model(input_dim)
        global_shared = get_shared_state(global_model)

        students = db.query(Student).all()
        client_states: List[dict] = []

        for s in students:
            X, y = get_student_feedback_dataset(db, s)
            if X.shape[0] < min_feedback:
                continue

            updated_shared = train_local(
                student=s,
                global_shared_state=global_shared,
                db=db,
                input_dim=input_dim,
                epochs=3,
            )
            if updated_shared is not None:
                client_states.append(updated_shared)

        if not client_states:
            print("No eligible clients for FL round (not enough feedback).")
            return

        new_shared = fed_avg(client_states)
        set_shared_state(global_model, new_shared)
        save_global_model(global_model)
        print("✅ Federated round completed and global semantic model updated.")

    finally:
        db.close()


if __name__ == "__main__":
    run_federated_round()
