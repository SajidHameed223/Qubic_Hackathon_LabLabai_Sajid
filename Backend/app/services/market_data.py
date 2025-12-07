# app/services/market_data.py

"""
Live Market Data Service

Fetches real-time cryptocurrency market data from external APIs.
"""

import httpx
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


# CoinGecko API (free, no API key needed)
COINGECKO_API = "https://api.coingecko.com/api/v3"

# Cache for market data (to avoid rate limiting)
_market_cache = {}
_cache_duration = timedelta(minutes=5)


async def get_crypto_price(symbol: str = "bitcoin") -> Dict[str, Any]:
    """
    Get live cryptocurrency price from CoinGecko.
    
    Common symbols: bitcoin, ethereum, cardano, etc.
    For Qubic, we'll use bitcoin as a reference for now.
    """
    cache_key = f"price_{symbol}"
    
    # Check cache
    if cache_key in _market_cache:
        cached_data, cached_time = _market_cache[cache_key]
        if datetime.utcnow() - cached_time < _cache_duration:
            return cached_data
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{COINGECKO_API}/simple/price",
                params={
                    "ids": symbol,
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                    "include_market_cap": "true",
                    "include_24hr_vol": "true"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    "ok": True,
                    "symbol": symbol,
                    "price_usd": data.get(symbol, {}).get("usd", 0),
                    "change_24h": data.get(symbol, {}).get("usd_24h_change", 0),
                    "market_cap": data.get(symbol, {}).get("usd_market_cap", 0),
                    "volume_24h": data.get(symbol, {}).get("usd_24h_vol", 0),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Cache the result
                _market_cache[cache_key] = (result, datetime.utcnow())
                return result
            else:
                return {
                    "ok": False,
                    "error": f"API returned {response.status_code}"
                }
                
    except Exception as e:
        return {
            "ok": False,
            "error": f"Failed to fetch price: {str(e)}"
        }


async def get_market_summary() -> Dict[str, Any]:
    """
    Get overall crypto market summary.
    """
    cache_key = "market_summary"
    
    # Check cache
    if cache_key in _market_cache:
        cached_data, cached_time = _market_cache[cache_key]
        if datetime.utcnow() - cached_time < _cache_duration:
            return cached_data
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{COINGECKO_API}/global")
            
            if response.status_code == 200:
                data = response.json().get("data", {})
                result = {
                    "ok": True,
                    "total_market_cap_usd": data.get("total_market_cap", {}).get("usd", 0),
                    "total_volume_24h_usd": data.get("total_volume", {}).get("usd", 0),
                    "btc_dominance": data.get("market_cap_percentage", {}).get("btc", 0),
                    "eth_dominance": data.get("market_cap_percentage", {}).get("eth", 0),
                    "active_cryptocurrencies": data.get("active_cryptocurrencies", 0),
                    "markets": data.get("markets", 0),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Cache the result
                _market_cache[cache_key] = (result, datetime.utcnow())
                return result
            else:
                return {
                    "ok": False,
                    "error": f"API returned {response.status_code}"
                }
                
    except Exception as e:
        return {
            "ok": False,
            "error": f"Failed to fetch market summary: {str(e)}"
        }


async def get_trending_coins() -> Dict[str, Any]:
    """Get trending cryptocurrencies"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{COINGECKO_API}/search/trending")
            
            if response.status_code == 200:
                data = response.json()
                trending = [
                    {
                        "name": coin["item"]["name"],
                        "symbol": coin["item"]["symbol"],
                        "price_btc": coin["item"].get("price_btc", 0),
                        "market_cap_rank": coin["item"].get("market_cap_rank")
                    }
                    for coin in data.get("coins", [])[:10]
                ]
                
                return {
                    "ok": True,
                    "trending": trending,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "ok": False,
                    "error": f"API returned {response.status_code}"
                }
                
    except Exception as e:
        return {
            "ok": False,
            "error": f"Failed to fetch trending: {str(e)}"
        }


def get_qubic_market_context() -> Dict[str, Any]:
    """
    Get Qubic-specific market context.
    
    For now, uses BTC as reference. Can be updated when Qubic is
    listed on CoinGecko or other APIs.
    """
    return {
        "note": "Using BTC as reference market data",
        "qubic_status": "Use Qubic RPC for network-specific data",
        "reference_asset": "bitcoin"
    }


async def get_comprehensive_market_data() -> Dict[str, Any]:
    """
    Get comprehensive market data for advisor context.
    """
    # Get multiple data points
    btc_price = await get_crypto_price("bitcoin")
    eth_price = await get_crypto_price("ethereum")
    market_summary = await get_market_summary()
    
    return {
        "btc": btc_price,
        "eth": eth_price,
        "market_summary": market_summary,
        "qubic_context": get_qubic_market_context(),
        "fetched_at": datetime.utcnow().isoformat()
    }
