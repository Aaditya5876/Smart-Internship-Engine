# app/api/v1/ml.py

from fastapi import APIRouter, Depends, status

from app.services.deps import require_admin
from app.ml.pfl_train import run_federated_round

router = APIRouter(prefix="/ml", tags=["ml"])


@router.post(
    "/run-fl-round",
    status_code=status.HTTP_202_ACCEPTED,
)
def run_fl_round(
    _: str = Depends(require_admin),
):
    """
    Trigger a single federated learning round (PFL/FL).

    - ADMIN only.
    - Runs synchronously for now (the request will block until the round finishes).
    """
    run_federated_round()
    return {"detail": "Federated learning round completed"}
