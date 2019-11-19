# Wallet Service

We support two types of wallet
* General Wallet
	* Wallet created using DApp.
* MetaMask Wallet
	* Wallet created using MetaMask.

It consist of following components

**User**  &rarr;* **Wallet**

**Wallet**  &rarr;* **Channel**

Wallet Creation, View and Register Wallet, Channel Creation For Third Party and Update Channel Transaction

### Wallet Creation

Creates wallet on Ethereum platform. Multiple wallet can be created by user. A wallet cannot be shared by two or more user.

### View and Register Wallet

View and Register wallet for a user.

### Channel Creation for third party and Add funds to channel.

Channel with funds is needed to use AI service in DApp. This component helps to create channel for third party and has capability to add funds to a channel.

### Update Channel Transaction

Once Blockchain Transaction is submitted successfully. It is in "PENDING" state. When it will get mined, is not certain. This component continuously check for transaction status("FAILED" or "SUCCESS") and updates in the database.
