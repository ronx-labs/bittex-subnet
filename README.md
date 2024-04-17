<div align="center">

# Bittex Subnet

</div>

## Overview

The idea behind Bittex subnet is to build a DEX providing the most competitive rate in the world, which is powered by Bittensor.

Miners are liquidity providers to the platform. They compete with each other for a better exchange rate to get more incentives.

At its core lies the smart contract which ensures the correct execution of each swap.

A swap is "atomic" in the Bittex, which means that liquidity providers deposit their funds for each individual swap transaction instead of to a pool. The "atomic swap" approach reduces the risk of impermanent loss and providing more efficient liquidity provision.

Bittex Subnet aims to be the go-to platform for users looking for the best exchange rates in the DeFi space.

## Architecture

### Introduction to Proof-of-Bid (PoB)

A crucial part of the subnet is to build proper mechanism that ensures not only the correct execution of each swap but also the proof of bid for miners.

We managed to build the PoB by utilizing smart contract. The smart contract stores miners' bid amounts for each swap and ensures the correct execution of each swap.

All transactions and bid information is public and transparent.

Validators evaluate miners' performance based on bdi information from the smart contract.

### PoB explained by sequence diagram

![Bittex Subnet Sequence Diagram](docs/Bittex%20Subnet%20Sequence%20Diagram.png)

### Scoring mechanism

Miners are scored by several factors.

- for each swap (70%)
  - bid amount
  - if top 3
  - if winner

- for the past 7 days (20%)
  - total exchange amount (sum of winning swap bid amounts)
  - total number of winning swaps

- for the lifetime (10%)
  - total exchange amount (sum of winning swap bid amounts)
  - total number of winning swaps
