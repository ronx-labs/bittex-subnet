# Bittex Subnet

## Overview
The concept behind Bittex is to establish a decentralized, feeless cryptocurrency exchange platform powered by Bittensor network.

Current centralized (CEXs) and decentralized exchanges (DEXs) each have their advantages and drawbacks. CEXs are prone to security breaches and often necessitate divulging personal information, while DEXs offer greater security and privacy through a peer-to-peer model but still impose transaction fees on users.

Our goal is to create the premier cryptocurrency exchange platform that is both decentralized and free of transaction fees. On our platform, users will be able to trade their tokens at the most competitive rates.

## Architecture

- Miners contribute their assets, providing liquidity to our platform without the need to deposit their funds into centralized wallets. Their assets remain in their own wallets without exposing any sensitive information. Miners are simply required to demonstrate their capability as exchangers, which is assessed by verified validators in a decentralized manner.

- Validators are responsible for assessing the miners' capabilities. They pose queries such as, "If I want to exchange 100 Ethereum USDT for Binance USDT, how much Binance USDT will you provide in return?" Miners respond based on their balance and the current estimated price. Those offering the most favorable rates are rewarded. Validators verify the miners' responses by requesting a real transaction. For instance, if a miner claims to offer 101 Binance USDT for 100 Ethereum USDT, the validator will provide a Binance address to which the miner is asked to send the 101 Binance USDT. Upon successful completion of the transaction, the validator confirms its validity and scores the miner accordingly, with higher scores for better prices. If the miner fails to send the 101 Binance USDT to the provided address, its answer is determined invalid and gets punished.

- End users initiate exchange requests through validators. A validator selects a miner offering the best rate for the transaction. For example, if a user wishes to make the exchange outlined above, the validator facilitates the exchange by transferring 101 Binance USDT to the user and 100 Ethereum USDT to the miner. This process differs from the verification stage, where the transferred Binance USDT would be returned to the miner. Importantly, miners remain unaware of whether they will receive Binance USDT or Ethereum USDT, as validators use the same query for both verification and actual user transactions.

Through this mechanism, our subnet ensures that end users receive the best possible exchange rates. The Bittex subnet aims to become the preferred platform for users seeking optimal exchange rates, thereby enhancing the popularity of the Bittensor network among a wider audience. The growing popularity of the Bittensor network is expected to spur the development of additional subnets, further accelerating AI advancement.
