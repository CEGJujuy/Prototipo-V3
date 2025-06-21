from flask import Flask, render_template, request, jsonify, session
import os
from datetime import datetime
import uuid

# Importar módulos del asistente
from src.nlp_processor import NLPProcessor
from src.knowledge_base import KnowledgeBase
from src.response_generator import ResponseGenerator
from src.analytics import Analytics
from src.security import SecurityManager

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Inicializar componentes del asistente
nlp_processor = NLPProcessor()
knowledge_base = KnowledgeBase()
response_generator = ResponseGenerator()
analytics = Analytics()
security_manager = SecurityManager()

# Almacenamiento temporal en memoria (sin persistencia)
conversations = {}
user_sessions = {}

@app.route('/')
def index():
    """Página principal del asistente"""
    return render_template('index.html')

@app.route('/chat')
def chat():
    """Interfaz de chat principal"""
    # Crear sesión si no existe
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session['start_time'] = datetime.now().isoformat()
        conversations[session['session_id']] = []
        user_sessions[session['session_id']] = {
            'questions_count': 0,
            'subjects_covered': set(),
            'start_time': datetime.now(),
            'last_activity': datetime.now()
        }
    
    return render_template('chat.html')

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Procesar pregunta del estudiante"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Pregunta vacía'})
        
        # Validar entrada
        if not security_manager.validate_question(question):
            return jsonify({'error': 'Pregunta contiene contenido inapropiado'})
        
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'Sesión no válida'})
        
        # Procesar pregunta con NLP
        processed_question = nlp_processor.process_question(question)
        
        # Buscar en base de conocimiento
        relevant_content = knowledge_base.search(processed_question)
        
        # Generar respuesta
        response_data = response_generator.generate_response(
            question, processed_question, relevant_content
        )
        
        # Guardar conversación en memoria
        conversation_entry = {
            'id': len(conversations[session_id]) + 1,
            'question': question,
            'response': response_data['response'],
            'subject': response_data.get('subject'),
            'confidence': response_data.get('confidence', 0.0),
            'timestamp': datetime.now().isoformat(),
            'feedback_rating': None
        }
        
        conversations[session_id].append(conversation_entry)
        
        # Actualizar estadísticas de sesión
        user_sessions[session_id]['questions_count'] += 1
        user_sessions[session_id]['subjects_covered'].add(response_data.get('subject', 'general'))
        user_sessions[session_id]['last_activity'] = datetime.now()
        
        # Actualizar analytics
        analytics.update_session_stats(session_id, response_data.get('subject'))
        
        return jsonify({
            'response': response_data['response'],
            'subject': response_data.get('subject'),
            'confidence': response_data.get('confidence', 0.0),
            'suggestions': response_data.get('suggestions', []),
            'resources': response_data.get('resources', []),
            'conversation_id': conversation_entry['id']
        })
        
    except Exception as e:
        app.logger.error(f"Error processing question: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'})

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Recibir feedback del usuario"""
    try:
        data = request.get_json()
        conversation_id = data.get('conversation_id')
        rating = data.get('rating')
        
        session_id = session.get('session_id')
        if session_id and session_id in conversations:
            # Buscar la conversación y actualizar rating
            for conv in conversations[session_id]:
                if conv['id'] == conversation_id:
                    conv['feedback_rating'] = rating
                    analytics.record_feedback(session_id, rating)
                    return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Conversación no encontrada'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/history')
def get_conversation_history():
    """Obtener historial de conversación de la sesión actual"""
    session_id = session.get('session_id')
    if session_id and session_id in conversations:
        return jsonify({
            'conversations': conversations[session_id],
            'session_stats': {
                'questions_count': user_sessions[session_id]['questions_count'],
                'subjects_covered': list(user_sessions[session_id]['subjects_covered']),
                'session_duration': str(datetime.now() - user_sessions[session_id]['start_time'])
            }
        })
    
    return jsonify({'conversations': [], 'session_stats': {}})

@app.route('/dashboard')
def dashboard():
    """Dashboard con estadísticas generales"""
    stats = analytics.get_general_stats()
    return render_template('dashboard.html', stats=stats)

@app.route('/knowledge')
def knowledge_view():
    """Vista de la base de conocimiento"""
    subjects = knowledge_base.get_subjects_summary()
    return render_template('knowledge.html', subjects=subjects)

@app.route('/api/subjects')
def get_subjects():
    """Obtener lista de materias disponibles"""
    subjects = knowledge_base.get_available_subjects()
    return jsonify({'subjects': subjects})

@app.route('/help')
def help_page():
    """Página de ayuda"""
    return render_template('help.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)