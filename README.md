<div align="center">

# Bittex Subnet

</div>

## Overview

Welcome to Bittex, a revolutionary decentralized exchange (DEX) powered by Bittensor, designed to offer the most competitive exchange rates globally. By leveraging the decentralized and dynamic capabilities of Bittensor, Bittex redefines liquidity provision and currency exchange on the blockchain.

At Bittex, we adopt an innovative approach to liquidity provision termed "atomic swaps."<br/>
Unlike traditional DEXs where liquidity providers (LPs) deposit funds into a pool, Bittex requires miners to deposit funds for each swap transaction. This approach significantly reduces the risk of impermanent loss and enhances the efficiency of liquidity provided by our miners.

Miners in the Bittex subnet act as liquidity providers, playing a key role in the platform's operations.
They participate in a competitive bidding process to fulfill swap requests initiated by users. In each swap, the bids from the top three miners are evaluated, with the best bid executing the swap. Miners are rewarded based on their bid amounts, and the winning miner receives an additional bonus. This structure motivates miners to offer more competitive exchange rates, thereby boosting the overall efficacy of our decentralized exchange.

The primary goal of Bittex is to enhance the user experience by providing exceptional exchange rates and reducing the risks associated with liquidity provision. By integrating directly with the Bittensor network, Bittex benefits from the decentralized, secure, and efficient framework that Bittensor offers, making it a cutting-edge solution in the DeFi space.

## Architecture

### Introduction to Proof of bid

Proof of bid (PoB) is an underlying protocol that makes sure everything on our platform runs smoothly. At its core lies the smart contract, which guarantees that swap transactions are executed accurately and in accordance with predetermined rules. The contract's integrity is verified and audited by CertiK, underscoring our commitment to a trustworthy platform.

- (bscscan link here)
- (certik link here)

### PoB explained by sequence diagram

<!-- ![Bittex Subnet Sequence Diagram](docs/Bittex%20Subnet%20Sequence%20Diagram.png) -->
<img src="docs/Bittex%20Subnet%20Sequence%20Diagram.png" alt="Bittex Subnet Sequence Diagram" style="width: 100%; max-width: 1000px">

### Scoring mechanism

Miners' scores are calculated based on their activity in each swap, with additional consideration for their ongoing and historical performance:

- Swap-Specific Scoring (85%): For each individual swap, a miner's score is determined by:
  - The bid amount.
  - Inclusion in the top three bids.
  - Being the winning bidder.

- Seven-Day Performance (10%): A miner's activity over the last week influences their score through:
  - The total volume of successful swaps in USD.
  - The number of swaps won.

- Overall Contributions (5%): Recognizing the miner's total tenure, this aspect includes:
  - The total volume of successful swaps in USD.
  - The number of swaps won.
