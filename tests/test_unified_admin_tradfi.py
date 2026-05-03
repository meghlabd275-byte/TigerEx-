# @file test_unified_admin_tradfi.py
# @description TigerEx test suite
# @author TigerEx Development Team

import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient


MODULE_PATH = Path('backend/unified-admin-control/src/main.py')
spec = importlib.util.spec_from_file_location('unified_admin_main', MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


client = TestClient(mod.app)


def admin_headers():
    token = mod.create_access_token(
        'admin-user',
        role='admin',
        extra={'permissions': ['all']},
    )
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

    import_pool = client.post(
        '/api/v1/admin/tradfi/liquidity-pools/import?reason=external+sync',
        headers=headers,
        json={
            'pool_name': 'SOL Backup Pool',
            'symbol': 'SOL-USDT',
            'liquidity_amount': 980000,
            'source_exchange': 'TigerEx',
        },
    )
    assert import_pool.status_code == 200
    assert import_pool.json()['pool']['imported'] is True


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


def test_role_fees_and_user_service_access():
    headers = admin_headers()
    fee_res = client.post(
        '/api/v1/admin/fees/roles',
        headers=headers,
        json={
            'role_name': 'market_maker',
            'maker_fee': 0.0001,
            'taker_fee': 0.0003,
            'withdrawal_fee_rate': 0.0004,
            'reason': 'volume incentive'
        },
    )
    assert fee_res.status_code == 200
    assert fee_res.json()['profile']['role_name'] == 'market_maker'

    access_res = client.post(
        '/api/v1/admin/users/service-access',
        headers=headers,
        json={
            'user_id': 'u-1001',
            'service_name': 'futures',
            'enabled': False,
            'reason': 'risk review',
        },
    )
    assert access_res.status_code == 200
    assert access_res.json()['access']['enabled'] is False


def test_tradfi_operate_endpoint_and_user_halt_resume():
    headers = admin_headers()
    operate_res = client.post(
        '/api/v1/admin/tradfi/operate',
        headers=headers,
        json={
            'operation': 'create_pair',
            'reason': 'ops console create',
            'payload': {
                'symbol': 'XRP-USDT',
                'base_asset': 'XRP',
                'quote_asset': 'USDT',
                'market_type': 'spot',
                'maker_fee': 0.0009,
                'taker_fee': 0.0011,
                'max_leverage': 2,
            },
        },
    )
    assert operate_res.status_code == 200
    assert operate_res.json()['result']['symbol'] == 'XRP-USDT'

    halt_res = client.post(
        '/api/v1/admin/users/u-2002/access/halt-all?reason=compliance+review',
        headers=headers,
    )
    assert halt_res.status_code == 200
    assert all(not entry['enabled'] for entry in halt_res.json()['updated'])

    resume_res = client.post(
        '/api/v1/admin/users/u-2002/access/resume-all?reason=review+completed',
        headers=headers,
    )
    assert resume_res.status_code == 200
    assert all(entry['enabled'] for entry in resume_res.json()['updated'])
# TigerEx Wallet API
class WalletAPI:
    @staticmethod
    def create(auth_token):
        wordlist = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
        return {'address': '0x' + os.urandom(20).hex(), 'seed': ' '.join(wordlist.split()[:24]), 'ownership': 'USER_OWNS'}
