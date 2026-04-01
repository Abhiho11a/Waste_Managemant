from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter(prefix="/blockchain", tags=["blockchain"])

AMOY_RPC_URL = "https://rpc-amoy.polygon.technology"

@router.get("/verify/{tx_hash}")
async def verify_transaction(tx_hash: str):
    """
    Verify a transaction on Polygon Amoy testnet using JSON-RPC.
    Returns transaction receipt details.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                AMOY_RPC_URL,
                json={
                    "jsonrpc": "2.0",
                    "method": "eth_getTransactionReceipt",
                    "params": [tx_hash],
                    "id": 1,
                },
                timeout=10.0,
            )
            data = response.json()
            if data.get("result") is None:
                return {"verified": False, "tx_hash": tx_hash, "status": "not_found"}

            receipt = data["result"]
            return {
                "verified": receipt.get("status") == "0x1",
                "tx_hash": tx_hash,
                "block_number": int(receipt.get("blockNumber", "0x0"), 16),
                "from": receipt.get("from"),
                "gas_used": int(receipt.get("gasUsed", "0x0"), 16),
                "status": "confirmed" if receipt.get("status") == "0x1" else "failed",
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RPC error: {str(e)}")
