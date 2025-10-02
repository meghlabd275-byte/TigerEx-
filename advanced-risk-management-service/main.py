from fastapi import FastAPI, HTTPException
from datetime import datetime
import numpy as np
from sklearn.ensemble import IsolationForest
from collections import defaultdict
import json
from typing import Dict, List, Any

app = FastAPI(title="TigerEx Advanced Risk Management Service")

# Risk Management State
risk_state = {
    'alerts': [],
    'risk_scores': defaultdict(dict),
    'fraud_detections': [],
    'portfolio_risks': defaultdict(dict),
    'stress_test_results': defaultdict(dict)
}

class RiskManagementEngine:
    def __init__(self):
        self.fraud_detector = IsolationForest(contamination=0.05, random_state=42)
        self.risk_thresholds = {
            'low': 30,
            'medium': 60,
            'high': 80,
            'critical': 95
        }
    
    def calculate_real_time_risk_score(self, user_id: str, activity_data: Dict) -> float:
        """Calculate real-time risk score based on user activity"""
        risk_factors = {
            'login_anomaly': self.detect_login_anomaly(activity_data),
            'transaction_velocity': self.analyze_transaction_velocity(activity_data),
            'amount_anomaly': self.detect_amount_anomaly(activity_data),
            'behavioral_anomaly': self.detect_behavioral_anomaly(activity_data),
            'geographic_anomaly': self.detect_geographic_anomaly(activity_data)
        }
        
        # Calculate weighted risk score
        weights = {
            'login_anomaly': 0.25,
            'transaction_velocity': 0.20,
            'amount_anomaly': 0.20,
            'behavioral_anomaly': 0.20,
            'geographic_anomaly': 0.15
        }
        
        total_risk = sum(risk_factors[factor] * weights[factor] for factor in risk_factors)
        
        return min(total_risk, 100)  # Cap at 100
    
    def detect_login_anomaly(self, activity_data: Dict) -> float:
        """Detect login anomalies"""
        risk_score = 0
        
        # Check for unusual login times
        login_hour = activity_data.get('login_hour', 12)
        if login_hour