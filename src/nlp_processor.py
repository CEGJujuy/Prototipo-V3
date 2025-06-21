import nltk
import spacy
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Dict, List, Tuple

class NLPProcessor:
    def __init__(self):
        self.setup_nltk()
        self.setup_spacy()
        self.setup_sentence_transformer()
        self.subject_keywords = self.load_subject_keywords()
        
    def setup_nltk(self):
        """Configurar NLTK"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
            
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger')
    
    def setup_spacy(self):
        """Configurar spaCy"""
        try:
            self.nlp = spacy.load("es_core_news_sm")
        except OSError:
            print("Modelo de español no encontrado. Usando procesamiento básico.")
            self.nlp = None
    
    def setup_sentence_transformer(self):
        """Configurar Sentence Transformer para embeddings semánticos"""
        try:
            self.sentence_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        except Exception as e:
            print(f"Error cargando sentence transformer: {e}")
            self.sentence_model = None
    
    def load_subject_keywords(self) -> Dict[str, List[str]]:
        """Cargar palabras clave por materia"""
        return {
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
        """Procesar pregunta completa"""
        # Limpiar texto
        cleaned_question = self.clean_text(question)
        
        # Detectar materia
        subject = self.detect_subject(cleaned_question)
        
        # Extraer entidades
        entities = self.extract_entities(cleaned_question)
        
        # Obtener palabras clave
        keywords = self.extract_keywords(cleaned_question)
        
        # Clasificar tipo de pregunta
        question_type = self.classify_question_type(cleaned_question)
        
        # Generar embedding semántico
        embedding = self.get_semantic_embedding(cleaned_question)
        
        return {
            'original': question,
            'cleaned': cleaned_question,
            'subject': subject,
            'entities': entities,
            'keywords': keywords,
            'question_type': question_type,
            'embedding': embedding
        }
    
    def clean_text(self, text: str) -> str:
        """Limpiar y normalizar texto"""
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover caracteres especiales pero mantener acentos
        text = re.sub(r'[^\w\sáéíóúñü¿?¡!]', '', text)
        
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def detect_subject(self, text: str) -> str:
        """Detectar materia basada en palabras clave"""
        subject_scores = {}
        
        for subject, keywords in self.subject_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            subject_scores[subject] = score
        
        # Retornar materia con mayor puntaje
        if subject_scores:
            best_subject = max(subject_scores, key=subject_scores.get)
            if subject_scores[best_subject] > 0:
                return best_subject
        
        return 'general'
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extraer entidades nombradas"""
        entities = []
        
        if self.nlp:
            try:
                doc = self.nlp(text)
                for ent in doc.ents:
                    entities.append({
                        'text': ent.text,
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char
                    })
            except Exception as e:
                print(f"Error extrayendo entidades: {e}")
        
        return entities
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extraer palabras clave importantes"""
        try:
            from nltk.tokenize import word_tokenize
            from nltk.corpus import stopwords
            from nltk.tag import pos_tag
            
            try:
                stop_words = set(stopwords.words('spanish'))
            except:
                stop_words = set(['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las'])
            
            tokens = word_tokenize(text)
            
            # Filtrar stopwords y obtener palabras importantes
            keywords = []
            pos_tags = pos_tag(tokens)
            
            for word, pos in pos_tags:
                if (len(word) > 2 and 
                    word not in stop_words and 
                    word.isalpha()):
                    keywords.append(word)
            
            return keywords[:10]  # Retornar top 10 keywords
            
        except Exception as e:
            # Fallback simple
            words = text.split()
            return [word for word in words if len(word) > 3][:10]
    
    def classify_question_type(self, text: str) -> str:
        """Clasificar tipo de pregunta"""
        question_patterns = {
            'definition': [r'que es', r'define', r'definicion', r'significa', r'concepto'],
            'explanation': [r'como', r'por que', r'explica', r'porque', r'como funciona'],
            'calculation': [r'calcula', r'resuelve', r'resultado', r'cuanto', r'resolver'],
            'comparison': [r'diferencia', r'compara', r'versus', r'mejor', r'entre'],
            'example': [r'ejemplo', r'casos', r'muestra', r'ejemplos'],
            'procedure': [r'pasos', r'proceso', r'metodo', r'procedimiento', r'como hacer']
        }
        
        for question_type, patterns in question_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return question_type
        
        return 'general'
    
    def get_semantic_embedding(self, text: str) -> np.ndarray:
        """Obtener embedding semántico del texto"""
        if self.sentence_model:
            try:
                embedding = self.sentence_model.encode([text])
                return embedding[0]
            except Exception as e:
                print(f"Error generando embedding: {e}")
        
        return np.array([])
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcular similitud semántica entre dos textos"""
        if self.sentence_model:
            try:
                embeddings = self.sentence_model.encode([text1, text2])
                similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
                return float(similarity)
            except Exception as e:
                print(f"Error calculando similitud: {e}")
        
        # Fallback usando TF-IDF
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except:
            return 0.0