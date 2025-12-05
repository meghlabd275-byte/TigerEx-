#!/usr/bin/env python3

"""
TigerEx Task Center & Rewards Service
Category: gamification
Description: Task completion system with rewards, achievements, and loyalty program
Features: Daily/weekly tasks, achievement badges, loyalty tiers, reward distribution
"""

from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta, date
import logging
import os
import uuid
import json
from typing import Dict, List, Optional, Any
from decimal import Decimal
from functools import wraps
from enum import Enum
import calendar

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tigerex')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'tiger-task-center-secret-key')

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SPECIAL = "special"
    ACHIEVEMENT = "achievement"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"

class RewardType(Enum):
    POINTS = "points"
    TRADING_FEE_DISCOUNT = "trading_fee_discount"
    BONUS_TOKEN = "bonus_token"
    VIP_DAYS = "vip_days"
    NFT = "nft"
    BADGE = "badge"

class LoyaltyTier(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

class Task(db.Model):
    __tablename__ = 'tiger_tasks'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    task_type = db.Column(db.Enum(TaskType), nullable=False)
    category = db.Column(db.String(50))  # trading, social, learning, security
    
    # Task requirements
    requirements = db.Column(db.JSON)  # What needs to be done
    target_value = db.Column(db.Integer)  # Target number (e.g., trade 5 times)
    current_value = db.Column(db.Integer, default=0)
    
    # Rewards
    reward_type = db.Column(db.Enum(RewardType), nullable=False)
    reward_value = db.Column(db.Numeric(20, 8))
    additional_rewards = db.Column(db.JSON)
    
    # Timing
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    reset_schedule = db.Column(db.String(20))  # daily, weekly, monthly
    
    # Difficulty and requirements
    difficulty = db.Column(db.String(20))  # easy, medium, hard
    required_tier = db.Column(db.Enum(LoyaltyTier))
    prerequisites = db.Column(db.JSON)  # Tasks that must be completed first
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_recurring = db.Column(db.Boolean, default=False)
    max_completions = db.Column(db.Integer)  # Max times user can complete
    
    # Metadata
    icon_url = db.Column(db.String(500))
    banner_url = db.Column(db.String(500))
    tags = db.Column(db.JSON)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserTaskProgress(db.Model):
    __tablename__ = 'tiger_user_task_progress'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), nullable=False)
    task_id = db.Column(db.String(50), db.ForeignKey('tiger_tasks.id'), nullable=False)
    
    # Progress tracking
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.PENDING)
    progress = db.Column(db.Integer, default=0)
    max_progress = db.Column(db.Integer)
    
    # Completion tracking
    completions = db.Column(db.Integer, default=0)
    first_completed_at = db.Column(db.DateTime)
    last_completed_at = db.Column(db.DateTime)
    
    # Reward tracking
    rewards_claimed = db.Column(db.Boolean, default=False)
    rewards_claimed_at = db.Column(db.DateTime)
    
    # Timestamps
    started_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    task = db.relationship('Task', backref='user_progress')

class Achievement(db.Model):
    __tablename__ = 'tiger_achievements'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    
    # Achievement criteria
    criteria = db.Column(db.JSON)  # Conditions to unlock
    check_type = db.Column(db.String(50))  # cumulative, streak, single_event
    
    # Rewards
    reward_type = db.Column(db.Enum(RewardType))
    reward_value = db.Column(db.Numeric(20, 8))
    badge_data = db.Column(db.JSON)  # Badge appearance data
    
    # Rarity and display
    rarity = db.Column(db.String(20))  # common, rare, epic, legendary
    points_value = db.Column(db.Integer)  # Achievement points
    is_hidden = db.Column(db.Boolean, default=False)
    
    # Social features
    shareable = db.Column(db.Boolean, default=True)
    celebration_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserAchievement(db.Model):
    __tablename__ = 'tiger_user_achievements'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), nullable=False)
    achievement_id = db.Column(db.String(50), db.ForeignKey('tiger_achievements.id'), nullable=False)
    
    # Unlock tracking
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.Column(db.JSON)  # Progress towards hidden achievements
    is_viewed = db.Column(db.Boolean, default=False)
    
    # Social
    shared = db.Column(db.Boolean, default=False)
    shared_at = db.Column(db.DateTime)
    
    achievement = db.relationship('Achievement', backref='user_unlocks')

class UserProfile(db.Model):
    __tablename__ = 'tiger_task_profiles'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    
    # Points and tier
    total_points = db.Column(db.Integer, default=0)
    current_tier = db.Column(db.Enum(LoyaltyTier), default=LoyaltyTier.BRONZE)
    tier_progress = db.Column(db.Integer, default=0)  # Progress towards next tier
    
    # Task statistics
    tasks_completed = db.Column(db.Integer, default=0)
    daily_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_task_date = db.Column(db.Date)
    
    # Achievement statistics
    achievements_unlocked = db.Column(db.Integer, default=0)
    total_achievement_points = db.Column(db.Integer, default=0)
    
    # Rewards tracking
    total_earned = db.Column(db.Numeric(20, 8), default=0)
    fee_discounts_available = db.Column(db.Numeric(5, 4), default=0)  # Discount percentage
    vip_days_remaining = db.Column(db.Integer, default=0)
    
    # Preferences
    notification_preferences = db.Column(db.JSON)
    favorite_task_categories = db.Column(db.JSON)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RewardHistory(db.Model):
    __tablename__ = 'tiger_reward_history'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), nullable=False)
    
    # Reward details
    reward_type = db.Column(db.Enum(RewardType), nullable=False)
    reward_value = db.Column(db.Numeric(20, 8))
    reward_data = db.Column(db.JSON)  # Additional reward data
    
    # Source
    source_type = db.Column(db.String(50))  # task, achievement, tier_up, bonus
    source_id = db.Column(db.String(50))  # ID of task/achievement
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, claimed, expired
    expires_at = db.Column(db.DateTime)
    claimed_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TaskCenterEngine:
    def __init__(self):
        self.loyalty_tiers = {
            LoyaltyTier.BRONZE: {'min_points': 0, 'fee_discount': 0.0},
            LoyaltyTier.SILVER: {'min_points': 1000, 'fee_discount': 0.1},
            LoyaltyTier.GOLD: {'min_points': 5000, 'fee_discount': 0.2},
            LoyaltyTier.PLATINUM: {'min_points': 15000, 'fee_discount': 0.3},
            LoyaltyTier.DIAMOND: {'min_points': 50000, 'fee_discount': 0.5}
        }
    
    def get_user_profile(self, user_id: str) -> UserProfile:
        """Get or create user profile"""
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.session.add(profile)
            db.session.commit()
        return profile
    
    def update_user_tier(self, user_id: str):
        """Update user's loyalty tier based on points"""
        profile = self.get_user_profile(user_id)
        
        # Determine current tier
        current_tier = LoyaltyTier.BRONZE
        for tier, requirements in self.loyalty_tiers.items():
            if profile.total_points >= requirements['min_points']:
                current_tier = tier
        
        # Update if tier changed
        if current_tier != profile.current_tier:
            profile.current_tier = current_tier
            profile.fee_discounts_available = self.loyalty_tiers[current_tier]['fee_discount']
            db.session.commit()
            
            # Grant tier-up reward
            self.grant_reward(
                user_id,
                RewardType.TRADING_FEE_DISCOUNT,
                Decimal(str(self.loyalty_tiers[current_tier]['fee_discount'])),
                'tier_up',
                current_tier.value
            )
    
    def grant_reward(self, user_id: str, reward_type: RewardType, 
                    reward_value: Decimal, source_type: str, source_id: str,
                    expires_in_days: int = None):
        """Grant a reward to a user"""
        
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        reward = RewardHistory(
            user_id=user_id,
            reward_type=reward_type,
            reward_value=reward_value,
            source_type=source_type,
            source_id=source_id,
            expires_at=expires_at
        )
        
        db.session.add(reward)
        
        # Update user profile based on reward type
        profile = self.get_user_profile(user_id)
        
        if reward_type == RewardType.POINTS:
            profile.total_points += int(reward_value)
            self.update_user_tier(user_id)
        
        elif reward_type == RewardType.TRADING_FEE_DISCOUNT:
            profile.fee_discounts_available = max(
                profile.fee_discounts_available, float(reward_value)
            )
        
        elif reward_type == RewardType.VIP_DAYS:
            profile.vip_days_remaining += int(reward_value)
        
        elif reward_type == RewardType.BADGE:
            profile.total_achievement_points += int(reward_value)
        
        profile.total_earned += reward_value
        db.session.commit()
        
        return reward
    
    def complete_task(self, user_id: str, task_id: str, progress_data: Dict = None):
        """Complete a task and grant rewards"""
        task = Task.query.get(task_id)
        if not task:
            return None, "Task not found"
        
        # Get or create user progress
        progress = UserTaskProgress.query.filter_by(
            user_id=user_id,
            task_id=task_id
        ).first()
        
        if not progress:
            progress = UserTaskProgress(
                user_id=user_id,
                task_id=task_id,
                max_progress=task.target_value
            )
            db.session.add(progress)
        
        # Update progress
        if progress_data:
            progress.progress = min(
                progress.progress + progress_data.get('increment', 1),
                task.target_value
            )
        
        # Check if completed
        if progress.progress >= task.target_value and progress.status != TaskStatus.COMPLETED:
            progress.status = TaskStatus.COMPLETED
            progress.last_completed_at = datetime.utcnow()
            
            if not progress.first_completed_at:
                progress.first_completed_at = datetime.utcnow()
            
            progress.completions += 1
            
            # Grant rewards
            reward = self.grant_reward(
                user_id,
                task.reward_type,
                task.reward_value,
                'task',
                task_id
            )
            
            # Update profile
            profile = self.get_user_profile(user_id)
            profile.tasks_completed += 1
            
            # Update daily streak
            today = date.today()
            if profile.last_task_date:
                if profile.last_task_date == today - timedelta(days=1):
                    profile.daily_streak += 1
                    profile.longest_streak = max(profile.longest_streak, profile.daily_streak)
                elif profile.last_task_date != today:
                    profile.daily_streak = 1
            else:
                profile.daily_streak = 1
            
            profile.last_task_date = today
            db.session.commit()
            
            return reward, "Task completed successfully"
        
        db.session.commit()
        return None, "Task progress updated"
    
    def check_achievements(self, user_id: str, event_type: str, event_data: Dict):
        """Check and unlock achievements based on user events"""
        profile = self.get_user_profile(user_id)
        
        # Get achievements that match the event type
        achievements = Achievement.query.filter(
            Achievement.criteria['event_type'].astext == event_type,
            ~Achievement.id.in_(
                db.session.query(UserAchievement.achievement_id).filter_by(user_id=user_id)
            )
        ).all()
        
        for achievement in achievements:
            if self.check_achievement_criteria(profile, achievement, event_data):
                # Unlock achievement
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id
                )
                db.session.add(user_achievement)
                
                # Grant achievement rewards
                if achievement.reward_type:
                    self.grant_reward(
                        user_id,
                        achievement.reward_type,
                        achievement.reward_value,
                        'achievement',
                        achievement.id
                    )
                
                # Update profile
                profile.achievements_unlocked += 1
                profile.total_achievement_points += achievement.points_value or 0
                
                db.session.commit()
                
                logger.info(f"User {user_id} unlocked achievement {achievement.name}")
    
    def check_achievement_criteria(self, profile: UserProfile, achievement: Achievement, event_data: Dict) -> bool:
        """Check if user meets achievement criteria"""
        criteria = achievement.criteria
        
        if achievement.check_type == 'cumulative':
            # Check cumulative stats
            if criteria.get('tasks_completed') and profile.tasks_completed < criteria['tasks_completed']:
                return False
            
            if criteria.get('total_points') and profile.total_points < criteria['total_points']:
                return False
            
            if criteria.get('daily_streak') and profile.daily_streak < criteria['daily_streak']:
                return False
            
            return True
        
        elif achievement.check_type == 'single_event':
            # Check single event data
            for key, value in criteria.items():
                if key != 'event_type' and event_data.get(key) < value:
                    return False
            
            return True
        
        return False
    
    def get_available_tasks(self, user_id: str) -> List[Dict]:
        """Get available tasks for a user"""
        profile = self.get_user_profile(user_id)
        now = datetime.utcnow()
        
        # Get active tasks
        tasks = Task.query.filter_by(is_active=True).all()
        
        available_tasks = []
        for task in tasks:
            # Check if user meets requirements
            if task.required_tier:
                tier_order = [LoyaltyTier.BRONZE, LoyaltyTier.SILVER, LoyaltyTier.GOLD, 
                             LoyaltyTier.PLATINUM, LoyaltyTier.DIAMOND]
                if tier_order.index(profile.current_tier) < tier_order.index(task.required_tier):
                    continue
            
            # Check timing
            if task.start_date and task.start_date > now:
                continue
            
            if task.end_date and task.end_date < now:
                continue
            
            # Get user progress
            progress = UserTaskProgress.query.filter_by(
                user_id=user_id,
                task_id=task.id
            ).first()
            
            # Check if user can complete again
            if task.max_completions and progress and progress.completions >= task.max_completions:
                continue
            
            available_tasks.append({
                'task': task,
                'progress': progress
            })
        
        return available_tasks

# Initialize the task center engine
task_engine = TaskCenterEngine()

# API Routes
@app.route('/api/v1/tasks', methods=['GET'])
@jwt_required()
def get_available_tasks():
    """Get available tasks for the user"""
    try:
        user_id = get_jwt_identity()
        category = request.args.get('category')
        task_type = request.args.get('type')
        
        available_tasks = task_engine.get_available_tasks(user_id)
        
        # Filter by category and type
        if category:
            available_tasks = [t for t in available_tasks if t['task'].category == category]
        
        if task_type:
            available_tasks = [t for t in available_tasks if t['task'].task_type.value == task_type]
        
        result = []
        for item in available_tasks:
            task = item['task']
            progress = item['progress']
            
            result.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'category': task.category,
                'task_type': task.task_type.value,
                'difficulty': task.difficulty,
                'target_value': task.target_value,
                'current_progress': progress.progress if progress else 0,
                'max_progress': task.target_value,
                'status': progress.status.value if progress else 'pending',
                'completions': progress.completions if progress else 0,
                'max_completions': task.max_completions,
                'reward_type': task.reward_type.value,
                'reward_value': str(task.reward_value),
                'additional_rewards': task.additional_rewards,
                'start_date': task.start_date.isoformat() if task.start_date else None,
                'end_date': task.end_date.isoformat() if task.end_date else None,
                'icon_url': task.icon_url,
                'banner_url': task.banner_url,
                'tags': task.tags
            })
        
        return jsonify({
            'success': True,
            'tasks': result
        })
        
    except Exception as e:
        logger.error(f"Error getting available tasks: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/tasks/<task_id>/complete', methods=['POST'])
@jwt_required()
def complete_task(task_id):
    """Complete a task or update progress"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        reward, message = task_engine.complete_task(user_id, task_id, data)
        
        response = {
            'success': True,
            'message': message
        }
        
        if reward:
            response['reward'] = {
                'type': reward.reward_type.value,
                'value': str(reward.reward_value),
                'status': reward.status
            }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/achievements', methods=['GET'])
@jwt_required()
def get_user_achievements():
    """Get user's achievements"""
    try:
        user_id = get_jwt_identity()
        
        user_achievements = db.session.query(UserAchievement).join(Achievement).filter(
            UserAchievement.user_id == user_id
        ).all()
        
        result = []
        for user_achievement in user_achievements:
            achievement = user_achievement.achievement
            
            result.append({
                'id': achievement.id,
                'name': achievement.name,
                'description': achievement.description,
                'category': achievement.category,
                'rarity': achievement.rarity,
                'points_value': achievement.points_value,
                'badge_data': achievement.badge_data,
                'unlocked_at': user_achievement.unlocked_at.isoformat(),
                'is_viewed': user_achievement.is_viewed,
                'shareable': achievement.shareable
            })
        
        return jsonify({
            'success': True,
            'achievements': result
        })
        
    except Exception as e:
        logger.error(f"Error getting user achievements: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Get user's task profile"""
    try:
        user_id = get_jwt_identity()
        profile = task_engine.get_user_profile(user_id)
        
        # Calculate progress to next tier
        current_tier = profile.current_tier
        tier_progress = 0
        next_tier = None
        
        tier_order = [LoyaltyTier.BRONZE, LoyaltyTier.SILVER, LoyaltyTier.GOLD, 
                     LoyaltyTier.PLATINUM, LoyaltyTier.DIAMOND]
        
        current_index = tier_order.index(current_tier)
        if current_index < len(tier_order) - 1:
            next_tier = tier_order[current_index + 1]
            current_tier_points = task_engine.loyalty_tiers[current_tier]['min_points']
            next_tier_points = task_engine.loyalty_tiers[next_tier]['min_points']
            
            if next_tier_points > current_tier_points:
                tier_progress = ((profile.total_points - current_tier_points) / 
                               (next_tier_points - current_tier_points)) * 100
        
        return jsonify({
            'success': True,
            'profile': {
                'total_points': profile.total_points,
                'current_tier': profile.current_tier.value,
                'tier_progress': round(tier_progress, 2),
                'next_tier': next_tier.value if next_tier else None,
                'tasks_completed': profile.tasks_completed,
                'daily_streak': profile.daily_streak,
                'longest_streak': profile.longest_streak,
                'achievements_unlocked': profile.achievements_unlocked,
                'total_achievement_points': profile.total_achievement_points,
                'total_earned': str(profile.total_earned),
                'fee_discounts_available': profile.fee_discounts_available,
                'vip_days_remaining': profile.vip_days_remaining,
                'notification_preferences': profile.notification_preferences or {},
                'favorite_task_categories': profile.favorite_task_categories or []
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/rewards', methods=['GET'])
@jwt_required()
def get_user_rewards():
    """Get user's reward history"""
    try:
        user_id = get_jwt_identity()
        status_filter = request.args.get('status')
        
        query = RewardHistory.query.filter_by(user_id=user_id)
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        rewards = query.order_by(RewardHistory.created_at.desc()).limit(50).all()
        
        return jsonify({
            'success': True,
            'rewards': [{
                'id': reward.id,
                'reward_type': reward.reward_type.value,
                'reward_value': str(reward.reward_value),
                'reward_data': reward.reward_data,
                'source_type': reward.source_type,
                'source_id': reward.source_id,
                'status': reward.status,
                'expires_at': reward.expires_at.isoformat() if reward.expires_at else None,
                'claimed_at': reward.claimed_at.isoformat() if reward.claimed_at else None,
                'created_at': reward.created_at.isoformat()
            } for reward in rewards]
        })
        
    except Exception as e:
        logger.error(f"Error getting user rewards: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/leaderboard', methods=['GET'])
@jwt_required()
def get_leaderboard():
    """Get task completion leaderboard"""
    try:
        period = request.args.get('period', 'all_time')  # daily, weekly, monthly, all_time
        limit = int(request.args.get('limit', 50))
        
        # For now, return all-time leaderboard
        # In production, you'd want period-specific leaderboards
        profiles = UserProfile.query.order_by(UserProfile.total_points.desc()).limit(limit).all()
        
        result = []
        for i, profile in enumerate(profiles, 1):
            result.append({
                'rank': i,
                'user_id': profile.user_id,
                'total_points': profile.total_points,
                'current_tier': profile.current_tier.value,
                'tasks_completed': profile.tasks_completed,
                'achievements_unlocked': profile.achievements_unlocked,
                'daily_streak': profile.daily_streak,
                'longest_streak': profile.longest_streak
            })
        
        return jsonify({
            'success': True,
            'leaderboard': result,
            'period': period
        })
        
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/events', methods=['POST'])
@jwt_required()
def track_user_event():
    """Track user events for achievement checking"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        event_type = data.get('event_type')
        event_data = data.get('event_data', {})
        
        if not event_type:
            return jsonify({'success': False, 'error': 'event_type is required'}), 400
        
        # Check achievements
        task_engine.check_achievements(user_id, event_type, event_data)
        
        return jsonify({
            'success': True,
            'message': 'Event tracked successfully'
        })
        
    except Exception as e:
        logger.error(f"Error tracking user event: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'task-center-service',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    port = int(os.getenv('PORT', 8004))
    app.run(host='0.0.0.0', port=port, debug=True)