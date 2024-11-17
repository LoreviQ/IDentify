from solana.rpc.api import Client
from solders.pubkey import Pubkey
import time
from typing import List
import networkx as nx
import matplotlib.pyplot as plt  
import streamlit as st
import pandas as pd
from streamlit_agraph import agraph, Node, Edge, Config

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
MAX_RETRIES = 3
END_AFTER = 5
RATE_LIMIT_DELAY = 2
SYSTEM_PROGRAM_ADDRESSES = {
    "11111111111111111111111111111111",  # System Program
    "ComputeBudget111111111111111111111111111111", # Compute Budget
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", # Token Program
    "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL", # Associated Token Program
}

solana_client = Client(SOLANA_RPC_URL, commitment="confirmed")

@st.cache_data(ttl=300)  # 5 minute cache
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


def get_connected_wallets(transactions: List, max: int = END_AFTER) -> pd.DataFrame:
    """Get connected wallets from transactions, returns DataFrame with wallet details"""
    wallet_data = []
    checked_transactions = 0
    discovered = 0
    status_placeholder = st.empty()
    
    for txn in transactions:
        checked_transactions += 1
        status_placeholder.text(f"Discovered {discovered} wallets")
        if checked_transactions > max:
            break
            
        time.sleep(RATE_LIMIT_DELAY)
        
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
            accounts = txn_details.value.transaction.transaction.message.account_keys
            meta = txn_details.value.transaction.meta
            pre_balances = meta.pre_balances
            post_balances = meta.post_balances
            pre_token_balances = meta.pre_token_balances if hasattr(meta, 'pre_token_balances') else []
            post_token_balances = meta.post_token_balances if hasattr(meta, 'post_token_balances') else []
            
            token_changes = {}
            for pre in pre_token_balances:
                account_idx = pre.account_index
                if account_idx not in token_changes:
                    token_changes[account_idx] = {}
                token_changes[account_idx][pre.mint] = -float(pre.ui_token_amount.amount)
                
            for post in post_token_balances:
                account_idx = post.account_index
                if account_idx not in token_changes:
                    token_changes[account_idx] = {}
                if post.mint in token_changes[account_idx]:
                    token_changes[account_idx][post.mint] += float(post.ui_token_amount.amount)
                else:
                    token_changes[account_idx][post.mint] = float(post.ui_token_amount.amount)
            
            for idx, account in enumerate(accounts):
                account_str = str(account)
                if account_str in SYSTEM_PROGRAM_ADDRESSES:
                    continue
                    
                sql_change = post_balances[idx] - pre_balances[idx]
                token_dict = token_changes.get(idx, {})
                
                # Find existing wallet in data
                existing_wallet = next((w for w in wallet_data if w['wallet'] == account_str), None)
                
                if existing_wallet is None:
                    wallet_data.append({
                        'wallet': account_str,
                        'transactions': 1,
                        'sql_change': sql_change,
                        'token_change': token_dict
                    })
                    discovered += 1
                else:
                    existing_wallet['transactions'] += 1
                    existing_wallet['sql_change'] += sql_change
                    # Merge token changes
                    for mint, amount in token_dict.items():
                        if mint not in existing_wallet['token_changes']:
                            existing_wallet['token_change'][mint] = amount
                        else:
                            existing_wallet['token_change'][mint] += amount
                    
    return pd.DataFrame(wallet_data)

def calculate_weight(wallets):
    """Calculate weight based on transaction count and balance"""
    # Create a copy to avoid modifying original
    df = wallets.copy()
    
    # Normalize transactions 
    max_txn = df['transactions'].max()
    min_txn = df['transactions'].min()
    
    if max_txn == min_txn:
        df['weight'] = 1
    else:
        df['weight'] = 1 + ((df['transactions'] - min_txn) / (max_txn - min_txn)) * 9
    
    # In future you can add more metrics here, for example:
    # if 'balance' in df.columns:
    #     normalized_balance = (df['balance'] - df['balance'].min()) / (df['balance'].max() - df['balance'].min())
    #     df['weight'] = df['weight'] * 0.7 + normalized_balance * 0.3
    
    return df

def streamlit_graph(wallet, df_related_wallets):
    nodes = []
    edges = []
    
    df_weighted = calculate_weight(df_related_wallets)
    
    # Add main wallet node
    nodes.append(Node(
        id=wallet, 
        label=wallet[:6]+"...", 
        size=25,
        color="#00ff1e",  # Main wallet in green
        labelColor="white",
        font={'color': 'white', 'size': 16}
    ))  
        
    # Add related wallet nodes and edges
    for _, row in df_weighted.iterrows():
        nodes.append(Node(
            id=row['wallet'],
            label=row['wallet'][:6]+"...",
            size=20,
            color="#97c2fc",
            labelColor="white",
            font={'color': 'white', 'size': 16}
        ))
        edges.append(Edge(
            source=wallet,
            target=row['wallet'],
            width=row['weight']
        ))
    
    config = Config(
        width=750,
        height=750,
        directed=False,
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        backgroundColor="#222222",  # Dark background
        linkHighlightBehavior=True,
        highlightColor="#F7A7A6",
        node={
            'labelProperty': 'label', 
            'renderLabel': True,
    }
    )
    
    return agraph(nodes=nodes, 
                 edges=edges, 
                 config=config)

def build_wallet_graph(wallet, df_related_wallets):
    """Build network graph from wallet and related wallet DataFrame"""
    G = nx.Graph()
    G.add_node(wallet)
    for _, row in df_related_wallets.iterrows():
        weight = row['transactions']  # Using transactions as weight
        G.add_edge(wallet, row['wallet'], weight=weight)
    return G

def draw_graph(wallet_graph):
    edges = wallet_graph.edges()
    weights = [wallet_graph[u][v]['weight'] for u,v in edges]
    labels = {node: node[:6] + "..." for node in wallet_graph.nodes()}
    plt.figure(figsize=(12, 8))
    nx.draw(wallet_graph, 
           labels=labels,
           with_labels=True,
           node_color='lightblue',
           node_size=1500,
           font_size=8,
           width=weights,
           font_weight='bold')
    plt.savefig('wallet_graph.png')
    plt.close() 

def streamlit_host():
    st.title("Solana Wallet Graph")
    wallet_address = st.text_input(
        "Enter Solana Wallet Address",
        value="EJwrQpygnFry5a2kYsdK9CoebZ5w3vDLSqs6KHq8Baam"
    )
    try:
        if not len(wallet_address) == 44:  # Basic Solana address validation
            st.error("Please enter a valid Solana wallet address")
            return
        if st.button("Generate Graph"):
            with st.spinner("Fetching transactions..."):
                transactions = get_transactions(wallet_address)
                
            with st.spinner("Analyzing connected wallets... (This takes a while since the free solana api has harsh rate limits, sorry)"):
                connected_wallets = get_connected_wallets(transactions)
                connected_wallets = connected_wallets[connected_wallets['wallet'] != wallet_address]
                
            with st.spinner("Building graph..."):
                streamlit_graph(wallet_address, connected_wallets)
                
            # Display connected wallets as a table
            st.subheader("Connected Wallets")
            connected_wallets_sorted = connected_wallets.sort_values('transactions', ascending=False)
            display_df = connected_wallets_sorted.copy()
            display_df['sql_change'] = display_df['sql_change'].apply(lambda x: f"{x/1e9:.3f} SOL")
            display_df['token_change'] = display_df['token_change'].apply(lambda x: ', '.join([f"{amount:.3f} {mint}" for mint, amount in x.items()]) if x else '')
            display_df.columns = ["Wallet", "Interactions", "SOL Change", "Token Changes"]
            st.dataframe(display_df)
    except Exception as e:
        st.error(str(e))

def test(wallet_address):
    transactions = get_transactions(wallet_address)
    connected_wallets = get_connected_wallets(transactions)
    del connected_wallets[wallet_address]
    wallet_graph = build_wallet_graph(wallet_address, connected_wallets)
    draw_graph(wallet_graph)

if __name__ == "__main__":
    streamlit_host()