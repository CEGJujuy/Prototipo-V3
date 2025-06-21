from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json

# Importar módulos del asistente
from src.nlp_processor import NLPProcessor
from src.knowledge_base import KnowledgeBase
from src.response_generator import ResponseGenerator
from src.analytics import Analytics
from src.security import SecurityManager

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///asistente_educativo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Inicializar componentes del asistente
nlp_processor = NLPProcessor()
knowledge_base = KnowledgeBase()
response_generator = ResponseGenerator()
analytics = Analytics()
security_manager = SecurityManager()

# Modelos de base de datos
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='student')  # student, teacher, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    conversations = db.relationship('Conversation', backref='user', lazy=True)
    analytics_data = db.relationship('UserAnalytics', backref='user', lazy=True)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    subject = db.Column(db.String(50))
    confidence_score = db.Column(db.Float)
    feedback_rating = db.Column(db.Integer)  # 1-5 rating
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(100))

class UserAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    questions_asked = db.Column(db.Integer, default=0)
    subjects_covered = db.Column(db.Text)  # JSON string
    avg_confidence = db.Column(db.Float)
    session_duration = db.Column(db.Integer)  # minutes

class KnowledgeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.Text)  # JSON string
    difficulty_level = db.Column(db.String(20))  # basic, intermediate, advanced
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rutas principales
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'student')
        
        # Validaciones de seguridad
        if not security_manager.validate_input(username) or not security_manager.validate_email(email):
            return jsonify({'success': False, 'message': 'Datos inválidos'})
        
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'El usuario ya existe'})
        
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'El email ya está registrado'})
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Usuario registrado exitosamente'})
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            user.last_active = datetime.utcnow()
            db.session.commit()
            return jsonify({'success': True, 'redirect': url_for('chat')})
        
        return jsonify({'success': False, 'message': 'Credenciales inválidas'})
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=current_user)

@app.route('/api/ask', methods=['POST'])
@login_required
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Pregunta vacía'})
        
        # Validar entrada
        if not security_manager.validate_question(question):
            return jsonify({'error': 'Pregunta contiene contenido inapropiado'})
        
        # Procesar pregunta con NLP
        processed_question = nlp_processor.process_question(question)
        
        # Buscar en base de conocimiento
        relevant_content = knowledge_base.search(processed_question)
        
        # Generar respuesta
        response_data = response_generator.generate_response(
            question, processed_question, relevant_content
        )
        
        # Guardar conversación
        conversation = Conversation(
            user_id=current_user.id,
            question=question,
            response=response_data['response'],
            subject=response_data.get('subject'),
            confidence_score=response_data.get('confidence', 0.0),
            session_id=session.get('session_id', 'default')
        )
        
        db.session.add(conversation)
        db.session.commit()
        
        # Actualizar analytics
        analytics.update_user_stats(current_user.id, response_data.get('subject'))
        
        return jsonify({
            'response': response_data['response'],
            'subject': response_data.get('subject'),
            'confidence': response_data.get('confidence', 0.0),
            'suggestions': response_data.get('suggestions', []),
            'resources': response_data.get('resources', [])
        })
        
    except Exception as e:
        app.logger.error(f"Error processing question: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'})

@app.route('/api/feedback', methods=['POST'])
@login_required
def submit_feedback():
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    rating = data.get('rating')
    
    conversation = Conversation.query.get(conversation_id)
    if conversation and conversation.user_id == current_user.id:
        conversation.feedback_rating = rating
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False})

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role not in ['teacher', 'admin']:
        return redirect(url_for('chat'))
    
    # Obtener estadísticas
    stats = analytics.get_dashboard_stats(current_user.id, current_user.role)
    return render_template('dashboard.html', stats=stats, user=current_user)

@app.route('/knowledge-base')
@login_required
def knowledge_base_view():
    if current_user.role not in ['teacher', 'admin']:
        return redirect(url_for('chat'))
    
    entries = KnowledgeEntry.query.filter_by(is_active=True).all()
    return render_template('knowledge_base.html', entries=entries, user=current_user)

@app.route('/api/knowledge', methods=['POST'])
@login_required
def add_knowledge():
    if current_user.role not in ['teacher', 'admin']:
        return jsonify({'error': 'No autorizado'})
    
    data = request.get_json()
    
    entry = KnowledgeEntry(
        subject=data.get('subject'),
        topic=data.get('topic'),
        content=data.get('content'),
        keywords=json.dumps(data.get('keywords', [])),
        difficulty_level=data.get('difficulty_level', 'basic'),
        created_by=current_user.id
    )
    
    db.session.add(entry)
    db.session.commit()
    
    # Actualizar índice de búsqueda
    knowledge_base.update_index()
    
    return jsonify({'success': True})

@app.route('/history')
@login_required
def conversation_history():
    conversations = Conversation.query.filter_by(user_id=current_user.id)\
                                    .order_by(Conversation.timestamp.desc())\
                                    .limit(50).all()
    return render_template('history.html', conversations=conversations, user=current_user)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Crear usuario admin por defecto
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@asistente.edu',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
    
    app.run(debug=True, host='0.0.0.0', port=5000)