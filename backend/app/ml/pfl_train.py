import copy
from typing import List

import numpy as np
import torch
import torch.nn as nn
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.models import Student
from app.ml.model import (
    init_global_model,
    load_global_model,
    save_global_model,
    get_shared_state,
    set_shared_state,
)
from app.ml.features import build_skill_vocab, get_student_feedback_dataset


def train_local(
    student: Student,
    global_shared_state,
    vocab,
    db: Session,
    input_dim: int,
    epochs: int = 3,
) -> dict:
    """
    Local training for one student (client).
    Returns updated shared state dict.
    """
    X, y = get_student_feedback_dataset(db, student, vocab)
    if X.shape[0] == 0:
        return None  # no feedback, skip

    X_tensor = torch.from_numpy(X)
    y_tensor = torch.from_numpy(y)

    # build local model and set global shared weights
    from app.ml.model import PFLRecommender

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

    # return updated shared state only (PFL: personal layers stay local)
    updated_shared = get_shared_state(local_model)
    return updated_shared


def fed_avg(states: List[dict]) -> dict:
    """Simple FedAvg over shared states."""
    avg_state = copy.deepcopy(states[0])
    for k in avg_state.keys():
        for s in states[1:]:
            avg_state[k] += s[k]
        avg_state[k] /= len(states)
    return avg_state


def run_federated_round(min_feedback: int = 3):
    """
    One FL round across all students with at least `min_feedback` records.
    """
    db = SessionLocal()
    try:
        # 1. Build skill vocabulary & infer input dimension
        vocab = build_skill_vocab(db)
        # Student vector len: len(vocab)+2; job vector len: len(vocab)+3
        input_dim = (len(vocab) + 2) + (len(vocab) + 3)

        # 2. Load or init global model
        global_model = load_global_model(input_dim)
        global_shared = get_shared_state(global_model)

        # 3. Select clients (students) with enough feedback
        students = db.query(Student).all()
        client_states = []
        for s in students:
            X, y = get_student_feedback_dataset(db, s, vocab)
            if X.shape[0] < min_feedback:
                continue  # skip clients with too little data

            updated_shared = train_local(
                student=s,
                global_shared_state=global_shared,
                vocab=vocab,
                db=db,
                input_dim=input_dim,
                epochs=3,
            )
            if updated_shared is not None:
                client_states.append(updated_shared)

        if not client_states:
            print("No eligible clients for FL round (not enough feedback).")
            return

        # 4. FedAvg aggregation
        new_shared = fed_avg(client_states)

        # 5. Update global model and save
        set_shared_state(global_model, new_shared)
        save_global_model(global_model)
        print("✅ Federated round completed and global model updated.")

    finally:
        db.close()


if __name__ == "__main__":
    run_federated_round()
