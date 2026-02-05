import argparse
import json
import os
import time
from aiohttp import web
import aiohttp_cors
from blockchain import Blockchain, MAX_SUPPLY
from wallet import Wallet, Transaction

blockchain = Blockchain()

async def get_chain(request):
    chain_data = [block.to_dict() for block in blockchain.chain]
    return web.json_response({
        'length': len(chain_data),
        'chain': chain_data,
        'validators': list(blockchain.validators),
        'reward_queue': list(blockchain.reward_queue),
        'supply': blockchain.get_total_supply(),
        'max_supply': MAX_SUPPLY
    })

async def new_transaction(request):
    try:
        data = await request.json()
        required = ['sender', 'receiver', 'amount']
        if not all(k in data for k in required):
            return web.json_response({'message': 'Missing values'}, status=400)
        
        # Validate amount is integer
        try:
            amount = int(data['amount'])
        except (ValueError, TypeError):
            return web.json_response({'message': 'Amount must be an integer'}, status=400)
        
        if amount <= 0:
            return web.json_response({'message': 'Amount must be positive'}, status=400)
        
        tx = Transaction(
            sender=data['sender'],
            receiver=data['receiver'],
            amount=amount,
            data=data.get('data'),
            signature=data.get('signature'),
            timestamp=data.get('timestamp')
        )
        
        if blockchain.add_transaction(tx):
            return web.json_response({'message': 'Transaction added'}, status=201)
        return web.json_response({'message': 'Invalid Transaction'}, status=400)
    except Exception as e:
         return web.json_response({'message': f'Error: {str(e)}'}, status=500)

async def get_mining_work(request):
    """
    Returns work for miners:
    - Current Pending Txs
    - Previous Hash
    - Difficulty
    - Suggested Timestamp
    """
    address = request.query.get('address')
    device_id = request.query.get('device_id', 'unknown')
    
    if not address:
        return web.json_response({'error': 'Address required'}, status=400)
    
    # Auto-register as active validator for rewards (with Anti-Sybil check)
    blockchain.register_validator(address, device_id)
        
    last_block = blockchain.get_last_block()
    
    # 1. Add Reward Tx to pending temporarily for templating?
    # Actually, the miner needs to include it hash calculation.
    # In V1 Miner Script, we can construct the block manually there or send pre-filled here.
    # Let's send a pre-filled template.
    
    # Calculate Reward
    current_txs = blockchain.get_pending_txs()
    
    # SYSTEM rewards are now handled ONLY in blockchain.py submit_block logic.
    # No more manual TX injection here to prevent double-inflation.
    block_txs = current_txs
    
    work = {
        "index": last_block.index + 1,
        "previous_hash": last_block.hash,
        "target": blockchain.target,
        "timestamp": time.time(),
        "transactions": block_txs,
        "validator": address 
    }
    
    return web.json_response(work)

async def submit_mining_solution(request):
    try:
        data = await request.json()
        # We expect a full block dict (extended with nonce)
        success = blockchain.submit_block(data)
        if success:
            return web.json_response({'message': 'Block Accepted', 'hash': blockchain.get_last_block().hash})
        else:
            return web.json_response({'message': 'Block Rejected (Invalid PoW or Stale)'}, status=400)
    except Exception as e:
        print(e)
        return web.json_response({'error': str(e)}, status=500)

async def get_balance(request):
    address = request.match_info.get('address', '')
    balance = blockchain.get_balance(address)
    return web.json_response({'address': address, 'balance': balance})

# Setup App and CORS
app = web.Application()

# Routes
app.router.add_get('/chain', get_chain)
app.router.add_post('/transactions/new', new_transaction)
app.router.add_get('/mining/get-work', get_mining_work)
app.router.add_post('/mining/submit', submit_mining_solution)
app.router.add_get('/balance/{address}', get_balance)

dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard')
if os.path.exists(dashboard_path):
    app.router.add_static('/dashboard', dashboard_path, show_index=True)
else:
    print(f"Warning: Dashboard directory NOT found at {dashboard_path}")

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(allow_credentials=True, expose_headers="*", allow_headers="*")
})
for route in list(app.router.routes()):
    if not isinstance(route.resource, web.StaticResource):
        cors.add(route)

if __name__ == '__main__':
    print("DEBUG: Main starting...")
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=5005, type=int)
    args = parser.parse_args()
    print(f"DEBUG: Attempting to start on port {args.port}")
    try:
        print("DEBUG: Calling web.run_app...")
        web.run_app(app, host='0.0.0.0', port=args.port)
        print("DEBUG: web.run_app returned normally.")
    except Exception as e:
        print(f"DEBUG: FATAL ERROR during web.run_app: {e}")
        import traceback
        traceback.print_exc()
    print("DEBUG: Process exiting.")
