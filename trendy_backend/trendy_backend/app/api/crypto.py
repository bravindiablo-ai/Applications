from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/crypto", tags=["crypto"])

@router.get("/")
async def get_crypto_prices() -> Dict[str, Any]:
    """Get cryptocurrency prices"""
    return {
        "prices": [
            {"symbol": "BTC", "name": "Bitcoin", "price": 45000.0, "change_24h": 2.5},
            {"symbol": "ETH", "name": "Ethereum", "price": 3000.0, "change_24h": 1.8},
            {"symbol": "SOL", "name": "Solana", "price": 120.0, "change_24h": 5.2}
        ],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/{symbol}")
async def get_crypto_detail(symbol: str) -> Dict[str, Any]:
    """Get specific cryptocurrency details"""
    mock_data = {
        "BTC": {"symbol": "BTC", "name": "Bitcoin", "price": 45000.0, "market_cap": 880000000000},
        "ETH": {"symbol": "ETH", "name": "Ethereum", "price": 3000.0, "market_cap": 360000000000},
        "SOL": {"symbol": "SOL", "name": "Solana", "price": 120.0, "market_cap": 52000000000}
    }
    
    if symbol.upper() not in mock_data:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")
    
    return mock_data[symbol.upper()]
