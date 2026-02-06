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
        
        tx = Transaction(
            sender=data['sender'],
            receiver=data['receiver'],
            amount=int(data['amount']),
            fee=int(data.get('fee', 1_000_000)), # Default to 0.01 HOME
            data=data.get('data'),
            signature=data.get('signature'),
            timestamp=data.get('timestamp')
        )
        
        if blockchain.add_transaction(tx):
            return web.json_response({'message': 'Transaction added'}, status=201)
        else:
            return web.json_response({'message': 'Invalid Transaction (Insufficient funds or low fee)'}, status=400)
    except Exception as e:
         return web.json_response({'message': f'Error: {str(e)}'}, status=500)

async def get_mining_work(request):
    address = request.query.get('address')
    device_id = request.query.get('device_id', 'unknown')
    if not address:
        return web.json_response({'error': 'Address required'}, status=400)
    
    blockchain.register_validator(address, device_id)
    last_block = blockchain.get_last_block()
    
    work = {
        "index": last_block.index + 1,
        "previous_hash": last_block.hash,
        "target": blockchain.target,
        "timestamp": time.time(),
        "transactions": blockchain.get_pending_txs(),
        "validator": address 
    }
    return web.json_response(work)

async def submit_mining_solution(request):
    try:
        data = await request.json()
        if blockchain.submit_block(data):
            return web.json_response({'message': 'Block Accepted', 'hash': blockchain.get_last_block().hash})
        return web.json_response({'message': 'Block Rejected (Invalid PoW or Stale)'}, status=400)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def get_block(request):
    try:
        index = int(request.match_info.get('index', 0))
        if 0 <= index < len(blockchain.chain):
            return web.json_response(blockchain.chain[index].to_dict())
        return web.json_response({'error': 'Block not found'}, status=404)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def get_blocks_range(request):
    try:
        start = int(request.query.get('start', 0))
        end = int(request.query.get('end', len(blockchain.chain)))
        if end - start > 100: end = start + 100
        blocks = [b.to_dict() for b in blockchain.chain[start:end]]
        return web.json_response({'start': start, 'end': start + len(blocks), 'blocks': blocks, 'total': len(blockchain.chain)})
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def get_balance(request):
    address = request.match_info.get('address', '')
    return web.json_response({'address': address, 'balance': blockchain.get_balance(address)})

async def get_mempool(request):
    return web.json_response({'count': len(blockchain.pending_transactions), 'transactions': blockchain.get_pending_txs()})

async def get_debug_state(request):
    return web.json_response({
        'chain_len': len(blockchain.chain),
        'balances_count': len(blockchain.balances),
        'top_balances': sorted(blockchain.balances.items(), key=lambda x: x[1], reverse=True)[:5],
        'nodes': list(blockchain.nodes)
    })

async def get_nodes(request):
    return web.json_response({'nodes': list(blockchain.nodes)})

async def register_node(request):
    try:
        data = await request.json()
        node_addr = data.get('address')
        if not node_addr: return web.json_response({'error': 'Missing address'}, status=400)
        blockchain.register_node(node_addr)
        return web.json_response({'message': 'Node registered successfully', 'total_nodes': len(blockchain.nodes)})
    except Exception as e:
         return web.json_response({'error': str(e)}, status=500)

def create_app():
    app = web.Application()
    app.router.add_get('/chain', get_chain)
    app.router.add_get('/mempool', get_mempool)
    app.router.add_get('/debug/state', get_debug_state)
    app.router.add_get('/nodes', get_nodes)
    app.router.add_post('/nodes/register', register_node)
    app.router.add_get('/block/{index}', get_block)
    app.router.add_get('/blocks/range', get_blocks_range)
    app.router.add_post('/transactions/new', new_transaction)
    app.router.add_get('/mining/get-work', get_mining_work)
    app.router.add_post('/mining/submit', submit_mining_solution)
    app.router.add_get('/balance/{address}', get_balance)
    
    dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard')
    if os.path.exists(dashboard_path):
        app.router.add_static('/dashboard', dashboard_path, show_index=True)
    
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(allow_credentials=True, expose_headers="*", allow_headers="*")
    })
    for route in list(app.router.routes()):
        if not isinstance(route.resource, web.StaticResource):
            cors.add(route)
    return app

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=5005, type=int)
    args = parser.parse_args()
    print(f"[*] Starting HomeChain Node on port {args.port}...")
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=args.port)
