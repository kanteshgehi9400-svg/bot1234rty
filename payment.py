import aiohttp
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "TTWYTUp1VEbTkQJcwnmujwsfKJ6Ud3Y3au")

# USDT TRC20 contract address
USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"


class PaymentChecker:
    def __init__(self):
        self.checked_txns = set()  # Track already used transactions

    async def check_payment(self, user_id: int, expected_amount: float) -> bool:
        """
        Check if a USDT TRC20 payment has been received
        Looks for transactions in the last 30 minutes
        """
        try:
            url = f"https://apilist.tronscanapi.com/api/token_trc20/transfers"
            params = {
                "toAddress": WALLET_ADDRESS,
                "tokenAddress": USDT_CONTRACT,
                "limit": 20,
                "start": 0,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        logger.error(f"TronScan API error: {resp.status}")
                        return False

                    data = await resp.json()
                    transactions = data.get("token_transfers", [])

                    # Check last 30 minutes
                    cutoff = datetime.now() - timedelta(minutes=30)

                    for txn in transactions:
                        txn_hash = txn.get("transaction_id", "")

                        # Skip already used transactions
                        if txn_hash in self.checked_txns:
                            continue

                        # Check timestamp
                        txn_time_ms = txn.get("block_ts", 0)
                        txn_time = datetime.fromtimestamp(txn_time_ms / 1000)
                        if txn_time < cutoff:
                            continue

                        # Check amount (USDT has 6 decimals)
                        amount_raw = int(txn.get("quant", 0))
                        amount_usdt = amount_raw / 1_000_000

                        # Allow small tolerance ($0.50)
                        if abs(amount_usdt - expected_amount) <= 0.50:
                            self.checked_txns.add(txn_hash)
                            logger.info(f"Payment confirmed: {amount_usdt} USDT for user {user_id}")
                            return True

            return False

        except Exception as e:
            logger.error(f"Payment check error: {e}")
            return False

    async def get_recent_transactions(self) -> list:
        """Get recent transactions for admin review"""
        try:
            url = f"https://apilist.tronscanapi.com/api/token_trc20/transfers"
            params = {
                "toAddress": WALLET_ADDRESS,
                "tokenAddress": USDT_CONTRACT,
                "limit": 10,
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    data = await resp.json()
                    return data.get("token_transfers", [])
        except Exception as e:
            logger.error(f"Error fetching transactions: {e}")
            return []
