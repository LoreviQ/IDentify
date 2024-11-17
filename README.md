# IDentify - Solana Wallet Network Explorer 🕵️‍♂️

IDentify is a web application that visualizes connections between Solana wallets by analyzing on-chain transactions and behavior. Think of it as a "six degrees of separation" explorer for crypto wallets!

## 🌟 [Try It Live](https://identify-solana.streamlit.app/)

## What it Does

- Takes any Solana wallet address as input
- Analyzes recent transactions to identify connected wallets
- Visualizes the network of connections in an interactive graph
- Shows detailed transaction statistics and token transfers
- Helps identify patterns and relationships between wallets

## 🛠️ Technical Details

Built using:
- Python
- Streamlit for the web interface
- Solana RPC API for blockchain data
- NetworkX & Streamlit-AGraph for network visualization
- Pandas for data processing

## 🚀 Future Development Directions

1. **Enhanced Analysis**
   - Machine learning to identify wallet behavioral patterns
   - Clustering of similar wallets
   - Detection of potential bot activities
   - NFT transaction analysis

2. **Features**
   - Multi-hop wallet exploration (friends of friends)
   - Historical transaction timeline
   - Token holdings breakdown
   - Integration with NFT marketplace data

3. **Performance**
   - Caching frequently accessed wallet data
   - Parallel transaction processing
   - Supporting alternative RPC providers
   - Batch transaction fetching

4. **Identity Intelligence**
   - Integration with known wallet labels (CEXs, protocols, etc.)
   - Risk scoring based on transaction patterns
   - Wallet activity categorization
   - Cross-chain identity mapping

## 🏃‍♂️ Quick Start

1. Enter any Solana wallet address
2. Click "Generate Graph"
3. Explore the interactive visualization
4. Check the detailed transaction table below

## ⚠️ Limitations

- Currently limited to recent transactions due to API rate limits
- Basic wallet relationship analysis
- Simple visualization of direct connections only

## 🤝 Contributing

This was built in a few hours for the Web3 AI London Hackathon, but there's lots of room for improvement! Feel free to fork, submit PRs, or suggest new features.

## 📝 License

MIT

---

Made by [Oliver Jay](https://github.com/LoreviQ)