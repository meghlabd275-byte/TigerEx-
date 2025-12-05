#!/usr/bin/env python3
"""
Tiger Academy Service
Category: education
Description: Comprehensive educational platform for cryptocurrency and blockchain learning
"""

from flask import Flask, request, jsonify, g, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
import uuid
import json
from decimal import Decimal
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tigerex')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(20), nullable=False)  # 'beginner', 'intermediate', 'advanced'
    duration_hours = db.Column(db.Integer, nullable=False)
    instructor = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), default=0)
    thumbnail_url = db.Column(db.String(500))
    video_url = db.Column(db.String(500))
    tags = db.Column(db.JSON)
    learning_objectives = db.Column(db.JSON)
    prerequisites = db.Column(db.JSON)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Lesson(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    video_url = db.Column(db.String(500))
    duration_minutes = db.Column(db.Integer)
    order_index = db.Column(db.Integer, nullable=False)
    lesson_type = db.Column(db.String(50), default='video')  # 'video', 'text', 'quiz', 'assignment'
    resources = db.Column(db.JSON)  # PDF links, code samples, etc.
    quiz_questions = db.Column(db.JSON)  # For quiz lessons
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserProgress(db.Model):
    __tablename__ = 'user_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'))
    completion_percentage = db.Column(db.Numeric(5, 2), default=0)
    status = db.Column(db.String(20), default='not_started')  # 'not_started', 'in_progress', 'completed'
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    last_accessed_at = db.Column(db.DateTime, default=datetime.utcnow)
    time_spent_minutes = db.Column(db.Integer, default=0)
    quiz_scores = db.Column(db.JSON)  # Track quiz scores
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Certificate(db.Model):
    __tablename__ = 'certificates'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    certificate_id = db.Column(db.String(100), unique=True, nullable=False)
    score = db.Column(db.Numeric(5, 2))
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    pdf_url = db.Column(db.String(500))
    is_verified = db.Column(db.Boolean, default=True)

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    attempt_number = db.Column(db.Integer, nullable=False)
    answers = db.Column(db.JSON, nullable=False)
    score = db.Column(db.Numeric(5, 2), nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    passed = db.Column(db.Boolean, nullable=False)
    time_taken_minutes = db.Column(db.Integer)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(500))
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.JSON)
    featured_image_url = db.Column(db.String(500))
    reading_time_minutes = db.Column(db.Integer)
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Tiger Academy Service',
        'version': '1.0.0'
    })

@app.route('/api/courses', methods=['GET'])
def get_courses():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    category = request.args.get('category')
    level = request.args.get('level')
    search = request.args.get('search')
    
    query = Course.query.filter_by(is_published=True)
    
    if category:
        query = query.filter_by(category=category)
    if level:
        query = query.filter_by(level=level)
    if search:
        query = query.filter(Course.title.ilike(f'%{search}%') | Course.description.ilike(f'%{search}%'))
    
    courses = query.order_by(Course.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'courses': [{
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'category': course.category,
            'level': course.level,
            'duration_hours': course.duration_hours,
            'instructor': course.instructor,
            'price': float(course.price),
            'thumbnail_url': course.thumbnail_url,
            'tags': course.tags,
            'learning_objectives': course.learning_objectives,
            'created_at': course.created_at.isoformat()
        } for course in courses.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': courses.total,
            'pages': courses.pages
        }
    })

@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.query.filter_by(id=course_id, is_published=True).first()
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order_index).all()
    
    return jsonify({
        'course': {
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'category': course.category,
            'level': course.level,
            'duration_hours': course.duration_hours,
            'instructor': course.instructor,
            'price': float(course.price),
            'thumbnail_url': course.thumbnail_url,
            'video_url': course.video_url,
            'tags': course.tags,
            'learning_objectives': course.learning_objectives,
            'prerequisites': course.prerequisites,
            'created_at': course.created_at.isoformat()
        },
        'lessons': [{
            'id': lesson.id,
            'title': lesson.title,
            'duration_minutes': lesson.duration_minutes,
            'order_index': lesson.order_index,
            'lesson_type': lesson.lesson_type,
            'created_at': lesson.created_at.isoformat()
        } for lesson in lessons]
    })

@app.route('/api/courses/<int:course_id>/enroll', methods=['POST'])
@jwt_required()
def enroll_course(course_id):
    user_id = get_jwt_identity()
    
    course = Course.query.filter_by(id=course_id, is_published=True).first()
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # Check if already enrolled
    existing_progress = UserProgress.query.filter_by(
        user_id=user_id, 
        course_id=course_id
    ).first()
    
    if existing_progress:
        return jsonify({'error': 'Already enrolled in this course'}), 400
    
    # Create enrollment
    progress = UserProgress(
        user_id=user_id,
        course_id=course_id,
        status='in_progress',
        started_at=datetime.utcnow()
    )
    
    db.session.add(progress)
    db.session.commit()
    
    return jsonify({
        'message': 'Successfully enrolled in course',
        'course_id': course_id,
        'enrollment_id': progress.id
    }), 201

@app.route('/api/my-courses', methods=['GET'])
@jwt_required()
def get_my_courses():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    progress_query = db.session.query(UserProgress, Course)\
        .join(Course, UserProgress.course_id == Course.id)\
        .filter(UserProgress.user_id == user_id)\
        .order_by(UserProgress.last_accessed_at.desc())
    
    progress_pagination = progress_query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'enrollments': [{
            'enrollment_id': progress.id,
            'course': {
                'id': course.id,
                'title': course.title,
                'description': course.description,
                'category': course.category,
                'level': course.level,
                'duration_hours': course.duration_hours,
                'instructor': course.instructor,
                'thumbnail_url': course.thumbnail_url
            },
            'progress': {
                'completion_percentage': float(progress.completion_percentage),
                'status': progress.status,
                'started_at': progress.started_at.isoformat() if progress.started_at else None,
                'completed_at': progress.completed_at.isoformat() if progress.completed_at else None,
                'last_accessed_at': progress.last_accessed_at.isoformat(),
                'time_spent_minutes': progress.time_spent_minutes
            }
        } for progress, course in progress_pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': progress_pagination.total,
            'pages': progress_pagination.pages
        }
    })

@app.route('/api/lessons/<int:lesson_id>', methods=['GET'])
@jwt_required()
def get_lesson(lesson_id):
    user_id = get_jwt_identity()
    
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404
    
    # Check if user is enrolled in the course
    enrollment = UserProgress.query.filter_by(
        user_id=user_id,
        course_id=lesson.course_id
    ).first()
    
    if not enrollment:
        return jsonify({'error': 'Not enrolled in this course'}), 403
    
    # Update last accessed time
    enrollment.last_accessed_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'lesson': {
            'id': lesson.id,
            'course_id': lesson.course_id,
            'title': lesson.title,
            'content': lesson.content,
            'video_url': lesson.video_url,
            'duration_minutes': lesson.duration_minutes,
            'lesson_type': lesson.lesson_type,
            'resources': lesson.resources,
            'quiz_questions': lesson.quiz_questions if lesson.lesson_type == 'quiz' else None
        }
    })

@app.route('/api/lessons/<int:lesson_id>/complete', methods=['POST'])
@jwt_required()
def complete_lesson(lesson_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404
    
    enrollment = UserProgress.query.filter_by(
        user_id=user_id,
        course_id=lesson.course_id
    ).first()
    
    if not enrollment:
        return jsonify({'error': 'Not enrolled in this course'}), 403
    
    # Update lesson progress
    lesson_progress = UserProgress.query.filter_by(
        user_id=user_id,
        course_id=lesson.course_id,
        lesson_id=lesson_id
    ).first()
    
    if not lesson_progress:
        lesson_progress = UserProgress(
            user_id=user_id,
            course_id=lesson.course_id,
            lesson_id=lesson_id,
            status='completed',
            completed_at=datetime.utcnow()
        )
        db.session.add(lesson_progress)
    else:
        lesson_progress.status = 'completed'
        lesson_progress.completed_at = datetime.utcnow()
        lesson_progress.completion_percentage = 100
    
    # Update time spent
    if data and 'time_spent_minutes' in data:
        enrollment.time_spent_minutes += data['time_spent_minutes']
    
    # Calculate course completion
    total_lessons = Lesson.query.filter_by(course_id=lesson.course_id).count()
    completed_lessons = UserProgress.query.filter_by(
        user_id=user_id,
        course_id=lesson.course_id,
        status='completed'
    ).count()
    
    completion_percentage = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
    enrollment.completion_percentage = completion_percentage
    
    if completion_percentage >= 100:
        enrollment.status = 'completed'
        enrollment.completed_at = datetime.utcnow()
        
        # Generate certificate if course has a passing requirement
        course = Course.query.get(lesson.course_id)
        if course and course.price > 0:  # Only issue certificates for paid courses
            generate_certificate(user_id, lesson.course_id)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Lesson completed successfully',
        'lesson_id': lesson_id,
        'course_completion_percentage': float(completion_percentage)
    })

def generate_certificate(user_id, course_id):
    """Generate certificate for completed course"""
    course = Course.query.get(course_id)
    if not course:
        return
    
    certificate_id = f"TA{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    
    certificate = Certificate(
        user_id=user_id,
        course_id=course_id,
        certificate_id=certificate_id,
        expires_at=datetime.utcnow().replace(year=datetime.utcnow().year + 2)
    )
    
    db.session.add(certificate)
    db.session.commit()

@app.route('/api/quiz/<int:lesson_id>/submit', methods=['POST'])
@jwt_required()
def submit_quiz(lesson_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'answers' not in data:
        return jsonify({'error': 'Answers are required'}), 400
    
    lesson = Lesson.query.get(lesson_id)
    if not lesson or lesson.lesson_type != 'quiz':
        return jsonify({'error': 'Lesson is not a quiz'}), 400
    
    enrollment = UserProgress.query.filter_by(
        user_id=user_id,
        course_id=lesson.course_id
    ).first()
    
    if not enrollment:
        return jsonify({'error': 'Not enrolled in this course'}), 403
    
    # Calculate score
    quiz_questions = lesson.quiz_questions or []
    total_questions = len(quiz_questions)
    correct_answers = 0
    
    for i, question in enumerate(quiz_questions):
        user_answer = data['answers'].get(str(i))
        if user_answer == question.get('correct_answer'):
            correct_answers += 1
    
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    passed = score >= 70  # 70% passing threshold
    
    # Get attempt number
    attempt_count = QuizAttempt.query.filter_by(
        user_id=user_id,
        lesson_id=lesson_id
    ).count()
    
    attempt = QuizAttempt(
        user_id=user_id,
        lesson_id=lesson_id,
        attempt_number=attempt_count + 1,
        answers=data['answers'],
        score=score,
        total_questions=total_questions,
        correct_answers=correct_answers,
        passed=passed,
        time_taken_minutes=data.get('time_taken_minutes')
    )
    
    db.session.add(attempt)
    
    # Update lesson progress with quiz score
    lesson_progress = UserProgress.query.filter_by(
        user_id=user_id,
        lesson_id=lesson_id
    ).first()
    
    if lesson_progress:
        if not lesson_progress.quiz_scores:
            lesson_progress.quiz_scores = []
        lesson_progress.quiz_scores.append({
            'attempt': attempt_count + 1,
            'score': float(score),
            'passed': passed,
            'date': datetime.utcnow().isoformat()
        })
    
    db.session.commit()
    
    return jsonify({
        'score': float(score),
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'passed': passed,
        'attempt_number': attempt_count + 1
    })

@app.route('/api/articles', methods=['GET'])
def get_articles():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = Article.query.filter_by(is_published=True)
    
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Article.title.ilike(f'%{search}%') | Article.content.ilike(f'%{search}%'))
    
    articles = query.order_by(Article.published_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'articles': [{
            'id': article.id,
            'title': article.title,
            'excerpt': article.excerpt,
            'author': article.author,
            'category': article.category,
            'tags': article.tags,
            'featured_image_url': article.featured_image_url,
            'reading_time_minutes': article.reading_time_minutes,
            'views': article.views,
            'likes': article.likes,
            'published_at': article.published_at.isoformat() if article.published_at else None
        } for article in articles.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': articles.total,
            'pages': articles.pages
        }
    })

@app.route('/api/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    article = Article.query.filter_by(id=article_id, is_published=True).first()
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    
    # Increment views
    article.views += 1
    db.session.commit()
    
    return jsonify({
        'article': {
            'id': article.id,
            'title': article.title,
            'content': article.content,
            'author': article.author,
            'category': article.category,
            'tags': article.tags,
            'featured_image_url': article.featured_image_url,
            'reading_time_minutes': article.reading_time_minutes,
            'views': article.views,
            'likes': article.likes,
            'published_at': article.published_at.isoformat() if article.published_at else None,
            'created_at': article.created_at.isoformat()
        }
    })

@app.route('/api/certificates', methods=['GET'])
@jwt_required()
def get_certificates():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    certificates = db.session.query(Certificate, Course)\
        .join(Course, Certificate.course_id == Course.id)\
        .filter(Certificate.user_id == user_id)\
        .order_by(Certificate.issued_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'certificates': [{
            'id': certificate.id,
            'certificate_id': certificate.certificate_id,
            'course': {
                'id': course.id,
                'title': course.title,
                'instructor': course.instructor
            },
            'score': float(certificate.score) if certificate.score else None,
            'issued_at': certificate.issued_at.isoformat(),
            'expires_at': certificate.expires_at.isoformat() if certificate.expires_at else None,
            'pdf_url': certificate.pdf_url
        } for certificate, course in certificates.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': certificates.total,
            'pages': certificates.pages
        }
    })

@app.route('/api/admin/courses', methods=['POST'])
@jwt_required()
def create_course():
    # Check admin permissions
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.email not in ['admin@tigerex.com']:
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    required_fields = ['title', 'description', 'category', 'level', 'duration_hours', 'instructor']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    course = Course(
        title=data['title'],
        description=data['description'],
        category=data['category'],
        level=data['level'],
        duration_hours=data['duration_hours'],
        instructor=data['instructor'],
        price=Decimal(str(data.get('price', 0))),
        thumbnail_url=data.get('thumbnail_url'),
        video_url=data.get('video_url'),
        tags=data.get('tags', []),
        learning_objectives=data.get('learning_objectives', []),
        prerequisites=data.get('prerequisites', []),
        is_published=data.get('is_published', False)
    )
    
    db.session.add(course)
    db.session.commit()
    
    return jsonify({
        'message': 'Course created successfully',
        'course_id': course.id
    }), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5004, debug=True)