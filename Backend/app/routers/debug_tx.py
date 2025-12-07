# app/routers/debug_tx.py

from fastapi import APIRouter
from ..services import qubic_client

router = APIRouter(prefix="/debug", tags=["debug"])


@router.post("/send-qu")
def debug_send_qu(destination_id: str, amount: int):
    """
    Debug endpoint to test QubiPy transaction signing.
    
    Example:
      POST /debug/send-qu
      {
        "destination_id": "UXUFAQMCXZPZBCZVXVDCVLBPSZWAMLZHMAVYMYZBWGZJJKIQPDYBFUFAEPHM",
        "amount": 1000000
      }
    """
    result = qubic_client.send_qu_to_identity(
        destination_id=destination_id,
        amount=amount,
        tick_offset=10
    )
    return result