from flask import Flask, render_template, request, jsonify, session
import os
from datetime import datetime
import uuid
import json
import re
import random
from typing import Dict, List, Tuple
import math

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Simulación de módulos de IA sin dependencias externas
class SimpleNLPProcessor:
    def __init__(self):
        self.subject_keywords = {
            'matematicas': [
                'ecuacion', 'algebra', 'geometria', 'calculo', 'trigonometria',
                'derivada', 'integral', 'funcion', 'grafica', 'numero', 'suma',
                'resta', 'multiplicacion', 'division', 'fraccion', 'decimal',
                'porcentaje', 'probabilidad', 'estadistica', 'pitagoras',
                'cuadratica', 'lineal', 'parabola', 'vertice'
            ],
            'fisica': [
                'fuerza', 'energia', 'movimiento', 'velocidad', 'aceleracion',
                'masa', 'peso', 'gravedad', 'presion', 'temperatura', 'calor',
                'luz', 'sonido', 'electricidad', 'magnetismo', 'onda', 'atomo',
                'molecula', 'newton', 'joule', 'watt', 'cinetica', 'potencial'
            ],
            'quimica': [
                'elemento', 'compuesto', 'molecula', 'atomo', 'ion', 'enlace',
                'reaccion', 'acido', 'base', 'sal', 'ph', 'oxidacion', 'reduccion',
                'tabla periodica', 'electron', 'proton', 'neutron', 'valencia',
                'formula', 'ecuacion quimica', 'ionico', 'covalente'
            ],
            'biologia': [
                'celula', 'organismo', 'tejido', 'organo', 'sistema', 'adn',
                'gen', 'cromosoma', 'evolucion', 'ecosistema', 'biodiversidad',
                'fotosintesis', 'respiracion', 'digestion', 'circulacion',
                'reproduccion', 'herencia', 'mutacion', 'especie', 'clorofila'
            ],
            'historia': [
                'epoca', 'siglo', 'guerra', 'revolucion', 'imperio', 'dinastia',
                'civilizacion', 'cultura', 'sociedad', 'politica', 'economia',
                'arte', 'religion', 'filosofia', 'descubrimiento', 'conquista',
                'independencia', 'democracia', 'dictadura', 'colonial'
            ],
            'geografia': [
                'continente', 'pais', 'ciudad', 'rio', 'montana', 'oceano',
                'clima', 'relieve', 'poblacion', 'capital', 'frontera',
                'latitud', 'longitud', 'meridiano', 'paralelo', 'mapa',
                'escala', 'proyeccion', 'coordenadas', 'territorio'
            ],
            'lengua': [
                'gramatica', 'sintaxis', 'morfologia', 'semantica', 'fonologia',
                'verbo', 'sustantivo', 'adjetivo', 'adverbio', 'preposicion',
                'conjuncion', 'articulo', 'pronombre', 'oracion', 'sujeto',
                'predicado', 'complemento', 'literatura', 'texto', 'redaccion'
            ]
        }
    
    def process_question(self, question: str) -> Dict:
        cleaned = question.lower().strip()
        subject = self.detect_subject(cleaned)
        question_type = self.classify_question_type(cleaned)
        keywords = self.extract_keywords(cleaned)
        
        return {
            'original': question,
            'cleaned': cleaned,
            'subject': subject,
            'question_type': question_type,
            'keywords': keywords
        }
    
    def detect_subject(self, text: str) -> str:
        subject_scores = {}
        for subject, keywords in self.subject_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            subject_scores[subject] = score
        
        if subject_scores:
            best_subject = max(subject_scores, key=subject_scores.get)
            if subject_scores[best_subject] > 0:
                return best_subject
        return 'general'
    
    def classify_question_type(self, text: str) -> str:
        if any(word in text for word in ['que es', 'define', 'definicion', 'significa']):
            return 'definition'
        elif any(word in text for word in ['como', 'por que', 'explica', 'porque']):
            return 'explanation'
        elif any(word in text for word in ['calcula', 'resuelve', 'resultado', 'cuanto']):
            return 'calculation'
        elif any(word in text for word in ['diferencia', 'compara', 'versus']):
            return 'comparison'
        elif any(word in text for word in ['ejemplo', 'casos', 'muestra']):
            return 'example'
        return 'general'
    
    def extract_keywords(self, text: str) -> List[str]:
        words = text.split()
        return [word for word in words if len(word) > 3][:10]

class SimpleKnowledgeBase:
    def __init__(self):
        self.knowledge_data = {
            'matematicas': [
                {
                    'id': 1,
                    'topic': 'Ecuaciones lineales',
                    'content': '''Una ecuación lineal es una igualdad matemática entre dos expresiones algebraicas, 
                    donde las variables tienen exponente 1. La forma general es ax + b = 0, donde 'a' y 'b' son 
                    constantes y 'x' es la variable. Para resolver: 1) Aislar la variable, 2) Realizar operaciones 
                    inversas, 3) Verificar la solución. Ejemplo: 2x + 5 = 11, entonces 2x = 6, por lo tanto x = 3.''',
                    'keywords': ['ecuacion', 'lineal', 'variable', 'resolver', 'algebra'],
                    'difficulty_level': 'basic'
                },
                {
                    'id': 2,
                    'topic': 'Teorema de Pitágoras',
                    'content': '''El teorema de Pitágoras establece que en un triángulo rectángulo, el cuadrado 
                    de la hipotenusa es igual a la suma de los cuadrados de los catetos. Fórmula: a² + b² = c², 
                    donde c es la hipotenusa y a, b son los catetos. Se usa para calcular distancias y en 
                    problemas de geometría. Ejemplo: si a=3 y b=4, entonces c² = 9 + 16 = 25, por lo tanto c=5.''',
                    'keywords': ['pitagoras', 'triangulo', 'rectangulo', 'hipotenusa', 'catetos'],
                    'difficulty_level': 'basic'
                }
            ],
            'fisica': [
                {
                    'id': 3,
                    'topic': 'Leyes de Newton',
                    'content': '''Las tres leyes de Newton son fundamentales en mecánica: 1) Primera ley (inercia): 
                    Un objeto en reposo permanece en reposo y uno en movimiento continúa en movimiento rectilíneo 
                    uniforme, a menos que actúe una fuerza externa. 2) Segunda ley: F = ma, la fuerza es igual 
                    a masa por aceleración. 3) Tercera ley: A toda acción corresponde una reacción igual y opuesta.''',
                    'keywords': ['newton', 'fuerza', 'inercia', 'aceleracion', 'masa'],
                    'difficulty_level': 'basic'
                }
            ],
            'quimica': [
                {
                    'id': 4,
                    'topic': 'Tabla periódica',
                    'content': '''La tabla periódica organiza los elementos químicos por número atómico creciente. 
                    Los elementos en la misma columna (grupo) tienen propiedades similares. Los períodos son las 
                    filas horizontales. Los grupos principales son: metales alcalinos (grupo 1), halógenos (grupo 17), 
                    gases nobles (grupo 18). Las propiedades periódicas incluyen radio atómico, energía de ionización.''',
                    'keywords': ['tabla', 'periodica', 'elementos', 'grupos', 'periodos'],
                    'difficulty_level': 'basic'
                }
            ],
            'biologia': [
                {
                    'id': 5,
                    'topic': 'La célula',
                    'content': '''La célula es la unidad básica de la vida. Tipos: procariotas (sin núcleo definido, 
                    como bacterias) y eucariotas (con núcleo, como plantas y animales). Partes principales de célula 
                    eucariota: membrana plasmática, citoplasma, núcleo, mitocondrias, retículo endoplasmático.''',
                    'keywords': ['celula', 'procariota', 'eucariota', 'nucleo', 'organelos'],
                    'difficulty_level': 'basic'
                }
            ]
        }
    
    def search(self, processed_question: Dict, top_k: int = 3) -> List[Dict]:
        subject = processed_question.get('subject', 'general')
        keywords = processed_question.get('keywords', [])
        
        results = []
        
        # Buscar en la materia detectada primero
        if subject in self.knowledge_data:
            for entry in self.knowledge_data[subject]:
                score = self.calculate_similarity(keywords, entry['keywords'])
                if score > 0:
                    result = entry.copy()
                    result['subject'] = subject
                    result['similarity'] = score
                    results.append(result)
        
        # Buscar en otras materias si no hay suficientes resultados
        if len(results) < top_k:
            for other_subject, entries in self.knowledge_data.items():
                if other_subject != subject:
                    for entry in entries:
                        score = self.calculate_similarity(keywords, entry['keywords'])
                        if score > 0:
                            result = entry.copy()
                            result['subject'] = other_subject
                            result['similarity'] = score * 0.7  # Penalizar por no ser la materia principal
                            results.append(result)
        
        # Ordenar por similitud y retornar top_k
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def calculate_similarity(self, keywords1: List[str], keywords2: List[str]) -> float:
        if not keywords1 or not keywords2:
            return 0.0
        
        common = set(keywords1) & set(keywords2)
        total = set(keywords1) | set(keywords2)
        
        return len(common) / len(total) if total else 0.0

class SimpleResponseGenerator:
    def __init__(self):
        self.response_templates = {
            'definition': [
                "Te explico qué es {topic}: {content}",
                "El concepto de {topic} se refiere a: {content}",
                "{topic} se define como: {content}"
            ],
            'explanation': [
                "Te explico cómo funciona {topic}: {content}",
                "Para entender {topic}, es importante saber que: {content}"
            ],
            'general': [
                "Sobre {topic}: {content}",
                "En relación a {topic}: {content}"
            ]
        }
        
        self.encouragement_phrases = [
            "¡Excelente pregunta!",
            "Me alegra que preguntes sobre esto.",
            "Es muy bueno que tengas curiosidad por este tema."
        ]
        
        self.learning_tips = [
            "💡 Consejo: Practica con ejercicios similares para reforzar este concepto.",
            "📚 Tip de estudio: Haz un resumen de los puntos clave.",
            "🎯 Recomendación: Relaciona este tema con ejemplos de la vida real."
        ]
    
    def generate_response(self, original_question: str, processed_question: Dict, 
                         relevant_content: List[Dict]) -> Dict:
        if not relevant_content:
            return self.generate_fallback_response(processed_question)
        
        best_match = relevant_content[0]
        subject = best_match['subject']
        topic = best_match['topic']
        content = best_match['content']
        confidence = best_match['similarity']
        
        question_type = processed_question.get('question_type', 'general')
        templates = self.response_templates.get(question_type, self.response_templates['general'])
        template = random.choice(templates)
        
        main_response = template.format(topic=topic, content=content)
        
        encouragement = random.choice(self.encouragement_phrases)
        learning_tip = random.choice(self.learning_tips)
        
        full_response = f"{encouragement}\n\n{main_response}\n\n{learning_tip}\n\n¿Te gustaría que profundice en algún aspecto específico?"
        
        suggestions = self.generate_suggestions(subject, topic)
        
        return {
            'response': full_response,
            'subject': subject,
            'topic': topic,
            'confidence': confidence,
            'suggestions': suggestions,
            'question_type': question_type
        }
    
    def generate_fallback_response(self, processed_question: Dict) -> Dict:
        subject = processed_question.get('subject', 'general')
        
        response = "Disculpa, no tengo información específica sobre esa consulta en mi base de conocimiento actual."
        
        if subject != 'general':
            response += f"\n\n¿Te interesa que te hable sobre otros temas de {subject}?"
        
        response += "\n\n💡 Consejo: Intenta reformular tu pregunta o ser más específico sobre el tema que te interesa."
        
        return {
            'response': response,
            'subject': subject,
            'topic': 'consulta_general',
            'confidence': 0.1,
            'suggestions': self.get_general_suggestions(subject),
            'question_type': 'general'
        }
    
    def generate_suggestions(self, subject: str, current_topic: str) -> List[str]:
        subject_suggestions = {
            'matematicas': [
                "¿Cómo resolver ecuaciones cuadráticas?",
                "¿Qué son las funciones lineales?",
                "¿Cómo calcular el área de figuras geométricas?"
            ],
            'fisica': [
                "¿Cómo calcular la velocidad y aceleración?",
                "¿Qué son las ondas y el sonido?",
                "¿Cómo funciona la electricidad?"
            ],
            'quimica': [
                "¿Cómo balancear ecuaciones químicas?",
                "¿Qué son los ácidos y bases?",
                "¿Cómo funciona la estructura atómica?"
            ],
            'biologia': [
                "¿Cómo funciona la respiración celular?",
                "¿Qué es la genética básica?",
                "¿Cómo funcionan los ecosistemas?"
            ]
        }
        
        return subject_suggestions.get(subject, [
            "¿Sobre qué materia te gustaría aprender?",
            "¿Necesitas ayuda con matemáticas, física, química o biología?"
        ])[:3]
    
    def get_general_suggestions(self, subject: str) -> List[str]:
        return self.generate_suggestions(subject, '')

class SimpleAnalytics:
    def __init__(self):
        self.session_stats = {}
        self.global_stats = {
            'total_questions': 0,
            'subjects_distribution': {},
            'feedback_ratings': [],
            'daily_usage': {}
        }
    
    def update_session_stats(self, session_id: str, subject: str):
        if session_id not in self.session_stats:
            self.session_stats[session_id] = {
                'questions_count': 0,
                'subjects_covered': set(),
                'start_time': datetime.now(),
                'confidence_scores': []
            }
        
        self.session_stats[session_id]['questions_count'] += 1
        self.session_stats[session_id]['subjects_covered'].add(subject)
        
        self.global_stats['total_questions'] += 1
        
        if subject not in self.global_stats['subjects_distribution']:
            self.global_stats['subjects_distribution'][subject] = 0
        self.global_stats['subjects_distribution'][subject] += 1
        
        today = datetime.now().date().isoformat()
        if today not in self.global_stats['daily_usage']:
            self.global_stats['daily_usage'][today] = 0
        self.global_stats['daily_usage'][today] += 1
    
    def record_feedback(self, session_id: str, rating: int):
        self.global_stats['feedback_ratings'].append({
            'rating': rating,
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id
        })
    
    def get_general_stats(self) -> Dict:
        active_sessions = len(self.session_stats)
        
        avg_feedback = 0
        if self.global_stats['feedback_ratings']:
            ratings = [f['rating'] for f in self.global_stats['feedback_ratings']]
            avg_feedback = sum(ratings) / len(ratings)
        
        sorted_subjects = sorted(
            self.global_stats['subjects_distribution'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            'total_questions': self.global_stats['total_questions'],
            'active_sessions': active_sessions,
            'average_session_time_minutes': 15,  # Simulado
            'average_confidence': 0.75,  # Simulado
            'average_feedback': avg_feedback,
            'subjects_distribution': dict(sorted_subjects),
            'top_subject': sorted_subjects[0][0] if sorted_subjects else 'N/A',
            'last_week_usage': self.get_last_week_usage(),
            'total_feedback_count': len(self.global_stats['feedback_ratings'])
        }
    
    def get_last_week_usage(self) -> Dict:
        # Simulación de datos de la última semana
        from datetime import timedelta
        last_week = {}
        today = datetime.now().date()
        
        for i in range(7):
            date = (today - timedelta(days=i)).isoformat()
            last_week[date] = self.global_stats['daily_usage'].get(date, 0)
        
        return last_week

# Inicializar componentes
nlp_processor = SimpleNLPProcessor()
knowledge_base = SimpleKnowledgeBase()
response_generator = SimpleResponseGenerator()
analytics = SimpleAnalytics()

# Almacenamiento en memoria
conversations = {}
user_sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
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
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Pregunta vacía'})
        
        if len(question) > 500:
            return jsonify({'error': 'Pregunta muy larga'})
        
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'Sesión no válida'})
        
        # Procesar pregunta
        processed_question = nlp_processor.process_question(question)
        
        # Buscar contenido relevante
        relevant_content = knowledge_base.search(processed_question)
        
        # Generar respuesta
        response_data = response_generator.generate_response(
            question, processed_question, relevant_content
        )
        
        # Guardar conversación
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
        
        # Actualizar estadísticas
        user_sessions[session_id]['questions_count'] += 1
        user_sessions[session_id]['subjects_covered'].add(response_data.get('subject', 'general'))
        user_sessions[session_id]['last_activity'] = datetime.now()
        
        analytics.update_session_stats(session_id, response_data.get('subject'))
        
        return jsonify({
            'response': response_data['response'],
            'subject': response_data.get('subject'),
            'confidence': response_data.get('confidence', 0.0),
            'suggestions': response_data.get('suggestions', []),
            'conversation_id': conversation_entry['id']
        })
        
    except Exception as e:
        app.logger.error(f"Error processing question: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'})

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json()
        conversation_id = data.get('conversation_id')
        rating = data.get('rating')
        
        session_id = session.get('session_id')
        if session_id and session_id in conversations:
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
    stats = analytics.get_general_stats()
    return render_template('dashboard.html', stats=stats)

@app.route('/knowledge')
def knowledge_view():
    subjects = {}
    for subject, entries in knowledge_base.knowledge_data.items():
        subjects[subject] = {
            'name': subject.title(),
            'topics_count': len(entries),
            'topics': [entry['topic'] for entry in entries]
        }
    return render_template('knowledge.html', subjects=subjects)

@app.route('/help')
def help_page():
    return render_template('help.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)