import logging
from typing import List, Optional, Dict, Any
import aiohttp
from config import COINGECKO_API_KEY

logger = logging.getLogger(__name__)

BASE_URL = "https://api.coingecko.com/api/v3"

class PriceService:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _get(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{BASE_URL}/{endpoint}"
        if COINGECKO_API_KEY:
            params["x_cg_pro_api_key"] = COINGECKO_API_KEY
        try:
            async with self.session.get(url, params=params) as resp:
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientError as e:
            logger.error(f"CoinGecko API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in API call: {e}")
            raise

    async def search_coin(self, query: str) -> Optional[Dict[str, str]]:
        """
        Search for a coin by symbol or name.
        Returns {'id': coin_id, 'symbol': symbol, 'name': name} or None.
        """
        try:
            data = await self._get("search", {"query": query})
            # First try to match symbol exactly, then name, then first result
            coins = data.get("coins", [])
            if not coins:
                return None
            # Prioritize exact symbol match
            query_lower = query.lower()
            for coin in coins:
                if coin.get("symbol", "").lower() == query_lower:
                    return {
                        "id": coin["id"],
                        "symbol": coin["symbol"].upper(),
                        "name": coin["name"]
                    }
            # If no exact symbol, use first result
            best = coins[0]
            return {
                "id": best["id"],
                "symbol": best["symbol"].upper(),
                "name": best["name"]
            }
        except Exception as e:
            logger.error(f"Search failed for '{query}': {e}")
            return None

    async def get_prices(self, coin_ids: List[str]) -> Dict[str, float]:
        """
        Fetch current USD prices for a list of CoinGecko ids.
        Returns dict {coin_id: price}
        """
        if not coin_ids:
            return {}
        try:
            ids = ",".join(coin_ids)
            params = {"ids": ids, "vs_currencies": "usd"}
            data = await self._get("simple/price", params)
            result = {}
            for coin_id, info in data.items():
                if "usd" in info:
                    result[coin_id] = info["usd"]
            return result
        except Exception as e:
            logger.error(f"Failed to fetch prices: {e}")
            return {}