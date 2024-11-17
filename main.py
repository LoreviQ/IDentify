from solana.rpc.api import Client
from solders.pubkey import Pubkey
import time
from typing import List

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
MAX_RETRIES = 3
RATE_LIMIT_DELAY = 1  # 500ms delay between requests

solana_client = Client(SOLANA_RPC_URL, commitment="confirmed")

def get_transactions(wallet_address: str) -> List:
    """Fetch confirmed transactions for the wallet"""
    pubkey = Pubkey.from_string(wallet_address)
    for attempt in range(MAX_RETRIES):
        try:
            response = solana_client.get_signatures_for_address(pubkey)
            if response and response.value:
                return response.value
            return []
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise e
            time.sleep(RATE_LIMIT_DELAY * (attempt + 1))


def get_connected_wallets(transactions: List, max: int= 10) -> List[str]:
    """Get connected wallets from transactions"""
    connected_wallets = set()
    failed = 0
    discovered = 0
    for txn in transactions:
        print(f"Discovered {discovered} wallets: {failed} failed")
        if discovered + failed >= max:
            break
        # Add delay to respect rate limits
        time.sleep(RATE_LIMIT_DELAY)
        
        # Fetch transaction details
        txn_details = solana_client.get_transaction(txn.signature, max_supported_transaction_version=0)
        if txn_details and txn_details.value:
            # Get accounts from transaction
            accounts = txn_details.value.transaction.transaction.message.account_keys
            # Add all account addresses to connected wallets
            for account in accounts:
                account_str = str(account)
                print(f"Discovered connected wallet: {account_str}")
                connected_wallets.add(account_str)
                discovered += 1
    return list(connected_wallets)


def main():
    test_adress = "EJwrQpygnFry5a2kYsdK9CoebZ5w3vDLSqs6KHq8Baam"
    transactions = get_transactions(test_adress)
    connected_wallets = get_connected_wallets(transactions)
    print(connected_wallets)

if __name__ == "__main__":
    main()