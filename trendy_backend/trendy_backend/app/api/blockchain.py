from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.database import get_db
import json
import hashlib
import time
import uuid

router = APIRouter()

class BlockchainService:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = {
            'index': 1,
            'timestamp': time.time(),
            'transactions': [],
            'proof': 1,
            'previous_hash': '0',
        }
        self.chain.append(genesis_block)
    
    def create_block(self, proof: int, previous_hash: str = None) -> Dict[str, Any]:
        """Create a new block"""
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block
    
    def hash(self, block: Dict[str, Any]) -> str:
        """Create SHA-256 hash of a block"""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def add_transaction(self, sender: str, receiver: str, amount: float, transaction_type: str) -> int:
        """Add a new transaction"""
        transaction = {
            'id': str(uuid.uuid4()),
            'sender': sender,
            'receiver': receiver,
            'amount': amount,
            'type': transaction_type,
            'timestamp': time.time()
        }
        self.current_transactions.append(transaction)
        return self.last_block['index'] + 1
    
    @property
    def last_block(self) -> Dict[str, Any]:
        """Return the last block in the chain"""
        return self.chain[-1]

# Initialize blockchain service
blockchain = BlockchainService()

@router.post("/blockchain/create-token")
async def create_creator_token(creator_id: str, token_name: str, initial_supply: float):
    """Create a new creator token on blockchain"""
    try:
        # Add token creation transaction
        blockchain.add_transaction(
            sender="system",
            receiver=creator_id,
            amount=initial_supply,
            transaction_type="token_creation"
        )
        
        # Create new block
        new_block = blockchain.create_block(proof=blockchain.last_block['proof'] + 1)
        
        return {
            "token_id": str(uuid.uuid4()),
            "creator_id": creator_id,
            "token_name": token_name,
            "initial_supply": initial_supply,
            "block_hash": blockchain.hash(new_block),
            "block_index": new_block['index']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/blockchain/transfer")
async def transfer_tokens(sender_id: str, receiver_id: str, amount: float, token_id: str):
    """Transfer tokens between users"""
    try:
        blockchain.add_transaction(
            sender=sender_id,
            receiver=receiver_id,
            amount=amount,
            transaction_type="token_transfer"
        )
        
        new_block = blockchain.create_block(proof=blockchain.last_block['proof'] + 1)
        
        return {
            "transaction_id": str(uuid.uuid4()),
            "sender": sender_id,
            "receiver": receiver_id,
            "amount": amount,
            "token_id": token_id,
            "block_hash": blockchain.hash(new_block)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/blockchain/balance/{user_id}")
async def get_token_balance(user_id: str):
    """Get user's token balance"""
    try:
        balance = 0
        for block in blockchain.chain:
            for transaction in block['transactions']:
                if transaction['receiver'] == user_id:
                    balance += transaction['amount']
                if transaction['sender'] == user_id:
                    balance -= transaction['amount']
        
        return {"user_id": user_id, "balance": balance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/blockchain/transactions/{user_id}")
async def get_user_transactions(user_id: str):
    """Get all transactions for a user"""
    try:
        transactions = []
        for block in blockchain.chain:
            for transaction in block['transactions']:
                if transaction['sender'] == user_id or transaction['receiver'] == user_id:
                    transactions.append(transaction)
        
        return {"user_id": user_id, "transactions": transactions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/blockchain/chain")
async def get_blockchain():
    """Get the entire blockchain"""
    return {
        "chain": blockchain.chain,
        "length": len(blockchain.chain)
    }
