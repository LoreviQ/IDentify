from solana.rpc.api import Client
from solders.pubkey import Pubkey 

solana_client = Client("https://api.mainnet-beta.solana.com")

def get_transactions(wallet_address):
    # Fetch confirmed transactions for the wallet
    pubkey = Pubkey.from_string(wallet_address)
    response = solana_client.get_signatures_for_address(pubkey)
    return response

def main():
    test_adress = "3GNJ8zxnqoe5FPncoqRe2gzAkvopmK7a8NzL2P5DF6yk"
    transactions = get_transactions(test_adress)
    print(transactions)

if __name__ == "__main__":
    main()