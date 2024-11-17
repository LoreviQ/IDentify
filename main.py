from solana.rpc.api import Client
from solders.pubkey import Pubkey
import time
from typing import List
import networkx as nx
from sklearn.cluster import DBSCAN
import numpy as np
import matplotlib.pyplot as plt  

def main(wallet_address):
    transactions = get_transactions(wallet_address)
    connected_wallets = get_connected_wallets(transactions)
    wallet_graph = build_wallet_graph(wallet_address, connected_wallets)
    
    # Create a new figure
    plt.figure(figsize=(12, 8))
    
    # Draw the graph
    nx.draw(wallet_graph, 
           with_labels=True,
           node_color='lightblue',
           node_size=1500,
           font_size=8,
           font_weight='bold')
    
    # Show the plot
    plt.show()

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
    connected_wallets = {}
    discovered = 0
    for txn in transactions:
        print(f"Discovered {discovered} wallets")
        if discovered >= max:
            break
        # Add delay to respect rate limits
        time.sleep(RATE_LIMIT_DELAY)
        
        # Try to fetch transaction details with retries
        txn_details = None
        for attempt in range(MAX_RETRIES):
            try:
                time.sleep(RATE_LIMIT_DELAY * (attempt + 1)) 
                txn_details = solana_client.get_transaction(txn.signature, max_supported_transaction_version=0)
                if txn_details:
                    break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for transaction {txn.signature}: {str(e)}")
                if attempt == MAX_RETRIES - 1:
                    print(f"All attempts failed for transaction {txn.signature}")
                    continue
        if txn_details and txn_details.value:
            # Get accounts from transaction
            accounts = txn_details.value.transaction.transaction.message.account_keys
            # Add all account addresses to connected wallets
            for account in accounts:
                account_str = str(account)
                print(f"Discovered connected wallet: {account_str}")
                if account_str in connected_wallets:
                    connected_wallets[account_str] += 1
                else:
                    connected_wallets[account_str] = 1
                    discovered += 1
    return connected_wallets

def build_wallet_graph(wallet, related_wallets):
    G = nx.Graph()
    G.add_node(wallet)
    for related, weight in related_wallets.items():
        G.add_edge(wallet, related, weight=weight)
    return G

def draw_graph(wallet_graph):
    edges = wallet_graph.edges()
    weights = [wallet_graph[u][v]['weight'] for u,v in edges]
    plt.figure(figsize=(12, 8))
    nx.draw(wallet_graph, 
           with_labels=True,
           node_color='lightblue',
           node_size=1500,
           font_size=8,
           width=weights,
           font_weight='bold')
    plt.savefig('wallet_graph.png')
    plt.close() 

def main(wallet_address):
    transactions = get_transactions(wallet_address)
    connected_wallets = get_connected_wallets(transactions)
    wallet_graph = build_wallet_graph(wallet_address, connected_wallets)
    draw_graph(wallet_graph)

if __name__ == "__main__":
    test_adress = "EJwrQpygnFry5a2kYsdK9CoebZ5w3vDLSqs6KHq8Baam"
    main(test_adress)