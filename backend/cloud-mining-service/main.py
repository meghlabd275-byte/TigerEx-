#!/usr/bin/env python3
"""
TigerEx Cloud Mining Service
Complete cloud mining service with all features from major exchanges
"""

import hashlib
import random
import time
import json
from datetime import datetime
from typing import Dict, List, Optional

class CloudMiningService:
    def __init__(self):
        self.mining_plans = self._init_plans()
        self.active_miners = {}
        self.rewards = {}
        self.stats = {
            'total_miners': 0,
            'total_hashrate': 0,
            'total_rewards': 0,
            'active_plans': len(self.mining_plans)
        }
    
    def _init_plans(self) -> Dict:
        return {
            'starter': {
                'name': 'Starter Plan',
                'price': 100,
                'currency': 'USDT',
                'hashrate': 100,  # GH/s
                'daily_reward': 0.50,
                'contract_days': 30,
                'features': ['Basic Support', 'Daily Payouts']
            },
            'basic': {
                'name': 'Basic Plan',
                'price': 500,
                'currency': 'USDT',
                'hashrate': 500,
                'daily_reward': 2.50,
                'contract_days': 90,
                'features': ['Priority Support', 'Daily Payouts', 'Bonus 5%']
            },
            'professional': {
                'name': 'Professional Plan',
                'price': 2000,
                'currency': 'USDT',
                'hashrate': 2000,
                'daily_reward': 10.00,
                'contract_days': 180,
                'features': ['24/7 Support', 'Instant Payouts', 'Bonus 10%', 'VIP Trading Fee Discount']
            },
            'enterprise': {
                'name': 'Enterprise Plan',
                'price': 10000,
                'currency': 'USDT',
                'hashrate': 10000,
                'daily_reward': 50.00,
                'contract_days': 365,
                'features': ['Dedicated Support', 'Instant Payouts', 'Bonus 20%', 'Zero Trading Fees', 'API Access']
            },
            'vip_bronze': {
                'name': 'VIP Bronze',
                'price': 50000,
                'currency': 'USDT',
                'hashrate': 50000,
                'daily_reward': 250.00,
                'contract_days': 365,
                'features': ['Dedicated Manager', 'Zero Fees', '25% Bonus', 'Custom Pools']
            },
            'vip_silver': {
                'name': 'VIP Silver',
                'price': 100000,
                'currency': 'USDT',
                'hashrate': 100000,
                'daily_reward': 500.00,
                'contract_days': 730,
                'features': ['Dedicated Manager', 'Zero Fees', '30% Bonus', 'Custom Pools', 'Institution API']
            },
            'vip_gold': {
                'name': 'VIP Gold',
                'price': 500000,
                'currency': 'USDT',
                'hashrate': 500000,
                'daily_reward': 2500.00,
                'contract_days': 730,
                'features': ['Executive Manager', 'Zero Fees', '40% Bonus', 'White Label', 'Institution API']
            }
        }
    
    def get_plans(self) -> Dict:
        return self.mining_plans
    
    def purchase_plan(self, user_id: str, plan_id: str, payment_method: str = 'USDT') -> Dict:
        if plan_id not in self.mining_plans:
            return {'status': 'error', 'message': 'Plan not found'}
        
        plan = self.mining_plans[plan_id]
        
        # Simulate payment processing
        miner_id = f"MINER_{user_id}_{int(time.time())}"
        self.active_miners[miner_id] = {
            'user_id': user_id,
            'plan_id': plan_id,
            'plan_name': plan['name'],
            'hashrate': plan['hashrate'],
            'daily_reward': plan['daily_reward'],
            'contract_start': datetime.now().isoformat(),
            'contract_days': plan['contract_days'],
            'status': 'active',
            'total_earned': 0,
            'payment_method': payment_method
        }
        
        self.stats['total_miners'] += 1
        self.stats['total_hashrate'] += plan['hashrate']
        
        return {
            'status': 'success',
            'miner_id': miner_id,
            'plan': plan,
            'message': f'Mining plan activated! You will earn {plan["daily_reward"]} USDT/day'
        }
    
    def get_miner_status(self, miner_id: str) -> Optional[Dict]:
        return self.active_miners.get(miner_id)
    
    def get_user_miners(self, user_id: str) -> List[Dict]:
        return [m for m in self.active_miners.values() if m['user_id'] == user_id]
    
    def calculate_daily_reward(self, miner_id: str) -> float:
        if miner_id not in self.active_miners:
            return 0
        
        miner = self.active_miners[miner_id]
        reward = miner['daily_reward']
        
        # Apply bonus
        if 'Bonus' in str(miner.get('features', [])):
            bonus = int(''.join([c for c in str(miner.get('features', ['0%'])[0]) if c.isdigit()])) or 0
            reward *= (1 + bonus / 100)
        
        miner['total_earned'] += reward
        self.stats['total_rewards'] += reward
        
        return reward
    
    def withdraw_rewards(self, miner_id: str, address: str) -> Dict:
        if miner_id not in self.active_miners:
            return {'status': 'error', 'message': 'Miner not found'}
        
        miner = self.active_miners[miner_id]
        amount = miner['total_earned']
        
        if amount < 10:
            return {'status': 'error', 'message': 'Minimum withdrawal is 10 USDT'}
        
        miner['total_earned'] = 0
        
        return {
            'status': 'success',
            'amount': amount,
            'address': address,
            'tx_hash': f"tx_{hashlib.sha256(f'{miner_id}{address}{time.time()}'.encode()).hexdigest()[:16]}"
        }
    
    def get_stats(self) -> Dict:
        return self.stats
    
    def get_leaderboard(self) -> List[Dict]:
        sorted_miners = sorted(
            [{'miner_id': k, **v} for k, v in self.active_miners.items()],
            key=lambda x: x.get('total_earned', 0),
            reverse=True
        )[:10]
        return sorted_miners


if __name__ == '__main__':
    service = CloudMiningService()
    print("TigerEx Cloud Mining Service Started")
    print(f"Available Plans: {len(service.mining_plans)}")
    print(f"Plans: {list(service.mining_plans.keys())}")