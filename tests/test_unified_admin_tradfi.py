import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient


MODULE_PATH = Path('backend/unified-admin-control/src/main.py')
spec = importlib.util.spec_from_file_location('unified_admin_main', MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


client = TestClient(mod.app)


def admin_headers():
    token = mod.create_access_token('admin-user', role='admin')
    return {'Authorization': f'Bearer {token}'}


def test_social_login_google():
    response = client.post(
        '/api/v1/auth/social/login',
        json={
            'provider': 'google',
            'provider_user_id': '1234',
            'email': 'user@example.com',
            'full_name': 'Tiger User',
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['token_type'] == 'bearer'
    assert body['user']['provider'] == 'google'


def test_admin_pair_and_pool_management_flow():
    headers = admin_headers()

    create_pair = client.post(
        '/api/v1/admin/tradfi/pairs?reason=initial+listing',
        headers=headers,
        json={
            'symbol': 'SOL-USDT',
            'base_asset': 'SOL',
            'quote_asset': 'USDT',
            'market_type': 'spot',
            'maker_fee': 0.0005,
            'taker_fee': 0.0007,
            'max_leverage': 3,
        },
    )
    assert create_pair.status_code == 200
    assert create_pair.json()['pair']['symbol'] == 'SOL-USDT'

    status_update = client.post(
        '/api/v1/admin/tradfi/pairs/SOL-USDT/status?status=halted&reason=maintenance',
        headers=headers,
    )
    assert status_update.status_code == 200

    list_pairs = client.get('/api/v1/admin/tradfi/pairs', headers=headers)
    assert list_pairs.status_code == 200
    assert any(p['symbol'] == 'SOL-USDT' and p['status'] == 'halted' for p in list_pairs.json()['pairs'])

    create_pool = client.post(
        '/api/v1/admin/tradfi/liquidity-pools?reason=bootstrap',
        headers=headers,
        json={
            'pool_name': 'SOL Primary Pool',
            'symbol': 'SOL-USDT',
            'liquidity_amount': 1200000,
            'source_exchange': 'bybit',
        },
    )
    assert create_pool.status_code == 200
    assert create_pool.json()['pool']['symbol'] == 'SOL-USDT'


def test_exchange_status_controls():
    headers = admin_headers()
    res = client.post(
        '/api/v1/admin/exchange/status',
        headers=headers,
        json={'exchange_id': 'tigerex-us', 'status': 'maintenance', 'reason': 'scheduled upgrade'},
    )
    assert res.status_code == 200

    get_res = client.get('/api/v1/admin/exchange/status/tigerex-us', headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()['status'] == 'maintenance'
