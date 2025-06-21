import json
from typing import List, Dict, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class KnowledgeBase:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words=None)
        self.tfidf_matrix = None
        self.documents = []
        self.load_initial_knowledge()
        self.build_search_index()
    
    def load_initial_knowledge(self):
        """Cargar conocimiento inicial por materias"""
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
                },
                {
                    'id': 3,
                    'topic': 'Funciones cuadráticas',
                    'content': '''Una función cuadrática tiene la forma f(x) = ax² + bx + c, donde a ≠ 0. 
                    Su gráfica es una parábola. El vértice está en x = -b/2a. El discriminante Δ = b² - 4ac 
                    determina el número de raíces reales. Si Δ > 0: dos raíces, Δ = 0: una raíz, Δ < 0: sin raíces reales.
                    La parábola abre hacia arriba si a > 0, hacia abajo si a < 0.''',
                    'keywords': ['funcion', 'cuadratica', 'parabola', 'vertice', 'discriminante'],
                    'difficulty_level': 'intermediate'
                }
            ],
            'fisica': [
                {
                    'id': 4,
                    'topic': 'Leyes de Newton',
                    'content': '''Las tres leyes de Newton son fundamentales en mecánica: 1) Primera ley (inercia): 
                    Un objeto en reposo permanece en reposo y uno en movimiento continúa en movimiento rectilíneo 
                    uniforme, a menos que actúe una fuerza externa. 2) Segunda ley: F = ma, la fuerza es igual 
                    a masa por aceleración. 3) Tercera ley: A toda acción corresponde una reacción igual y opuesta.
                    Estas leyes explican el comportamiento de los objetos en movimiento.''',
                    'keywords': ['newton', 'fuerza', 'inercia', 'aceleracion', 'masa'],
                    'difficulty_level': 'basic'
                },
                {
                    'id': 5,
                    'topic': 'Energía cinética y potencial',
                    'content': '''La energía cinética es la energía que posee un objeto debido a su movimiento: 
                    Ec = ½mv². La energía potencial gravitatoria es la energía almacenada debido a la posición: 
                    Ep = mgh. La energía mecánica total se conserva en ausencia de fuerzas no conservativas: 
                    Em = Ec + Ep = constante. Ejemplo: una pelota en el aire intercambia energía cinética y potencial.''',
                    'keywords': ['energia', 'cinetica', 'potencial', 'movimiento', 'conservacion'],
                    'difficulty_level': 'intermediate'
                }
            ],
            'quimica': [
                {
                    'id': 6,
                    'topic': 'Tabla periódica',
                    'content': '''La tabla periódica organiza los elementos químicos por número atómico creciente. 
                    Los elementos en la misma columna (grupo) tienen propiedades similares. Los períodos son las 
                    filas horizontales. Los grupos principales son: metales alcalinos (grupo 1), halógenos (grupo 17), 
                    gases nobles (grupo 18). Las propiedades periódicas incluyen radio atómico, energía de ionización.
                    Fue creada por Mendeleev y es fundamental para entender la química.''',
                    'keywords': ['tabla', 'periodica', 'elementos', 'grupos', 'periodos'],
                    'difficulty_level': 'basic'
                },
                {
                    'id': 7,
                    'topic': 'Enlaces químicos',
                    'content': '''Los enlaces químicos unen átomos para formar compuestos. Tipos principales: 
                    1) Enlace iónico: transferencia de electrones entre metal y no metal. 2) Enlace covalente: 
                    compartición de electrones entre no metales. 3) Enlace metálico: mar de electrones en metales. 
                    La electronegatividad determina el tipo de enlace. Los enlaces determinan las propiedades de los compuestos.''',
                    'keywords': ['enlace', 'ionico', 'covalente', 'metalico', 'electronegatividad'],
                    'difficulty_level': 'intermediate'
                }
            ],
            'biologia': [
                {
                    'id': 8,
                    'topic': 'La célula',
                    'content': '''La célula es la unidad básica de la vida. Tipos: procariotas (sin núcleo definido, 
                    como bacterias) y eucariotas (con núcleo, como plantas y animales). Partes principales de célula 
                    eucariota: membrana plasmática, citoplasma, núcleo, mitocondrias, retículo endoplasmático, 
                    aparato de Golgi, ribosomas. En plantas también: cloroplastos y pared celular. Todas las funciones vitales ocurren en la célula.''',
                    'keywords': ['celula', 'procariota', 'eucariota', 'nucleo', 'organelos'],
                    'difficulty_level': 'basic'
                },
                {
                    'id': 9,
                    'topic': 'Fotosíntesis',
                    'content': '''La fotosíntesis es el proceso por el cual las plantas convierten luz solar, 
                    CO₂ y agua en glucosa y oxígeno. Ecuación: 6CO₂ + 6H₂O + luz → C₆H₁₂O₆ + 6O₂. 
                    Ocurre en cloroplastos, tiene dos fases: reacciones lumínicas (tilacoides) y ciclo de Calvin (estroma). 
                    Es fundamental para la vida en la Tierra ya que produce oxígeno y alimento.''',
                    'keywords': ['fotosintesis', 'clorofila', 'glucosa', 'oxigeno', 'cloroplastos'],
                    'difficulty_level': 'intermediate'
                }
            ],
            'historia': [
                {
                    'id': 10,
                    'topic': 'Revolución Industrial',
                    'content': '''La Revolución Industrial (siglos XVIII-XIX) transformó la sociedad agraria en industrial. 
                    Comenzó en Inglaterra con la máquina de vapor, textiles y ferrocarriles. Cambios: urbanización, 
                    nuevas clases sociales (burguesía y proletariado), avances tecnológicos. Consecuencias: mejora en 
                    producción, pero también problemas laborales y ambientales. Marcó el inicio de la era moderna.''',
                    'keywords': ['revolucion', 'industrial', 'maquina', 'vapor', 'urbanizacion'],
                    'difficulty_level': 'intermediate'
                }
            ],
            'geografia': [
                {
                    'id': 11,
                    'topic': 'Coordenadas geográficas',
                    'content': '''Las coordenadas geográficas son un sistema para localizar cualquier punto en la Tierra. 
                    Latitud: distancia angular desde el Ecuador (0° a 90° Norte o Sur). Longitud: distancia angular 
                    desde el meridiano de Greenwich (0° a 180° Este u Oeste). Se expresan en grados, minutos y segundos. 
                    Permiten ubicación precisa usando GPS y mapas.''',
                    'keywords': ['coordenadas', 'latitud', 'longitud', 'meridiano', 'paralelo'],
                    'difficulty_level': 'basic'
                }
            ],
            'lengua': [
                {
                    'id': 12,
                    'topic': 'Análisis sintáctico',
                    'content': '''El análisis sintáctico estudia la estructura de las oraciones. Elementos principales: 
                    Sujeto (quien realiza la acción) y Predicado (lo que se dice del sujeto). El sujeto puede ser 
                    simple, compuesto o tácito. El predicado puede ser verbal o nominal. Complementos: directo, 
                    indirecto, circunstancial. Permite entender cómo se organizan las palabras para crear significado.''',
                    'keywords': ['sintaxis', 'sujeto', 'predicado', 'complemento', 'oracion'],
                    'difficulty_level': 'intermediate'
                }
            ]
        }
    
    def build_search_index(self):
        """Construir índice de búsqueda TF-IDF"""
        self.documents = []
        
        for subject, entries in self.knowledge_data.items():
            for entry in entries:
                # Combinar tema y contenido para búsqueda
                combined_text = f"{entry['topic']} {entry['content']}"
                self.documents.append({
                    'id': entry['id'],
                    'subject': subject,
                    'topic': entry['topic'],
                    'content': entry['content'],
                    'keywords': entry['keywords'],
                    'difficulty_level': entry['difficulty_level'],
                    'text': combined_text
                })
        
        if self.documents:
            texts = [doc['text'] for doc in self.documents]
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)
    
    def search(self, processed_question: Dict, top_k: int = 3) -> List[Dict]:
        """Buscar contenido relevante basado en la pregunta procesada"""
        if not self.documents or self.tfidf_matrix is None:
            return []
        
        query_text = processed_question.get('cleaned', '')
        subject = processed_question.get('subject', 'general')
        
        # Vectorizar la consulta
        query_vector = self.vectorizer.transform([query_text])
        
        # Calcular similitudes
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Obtener índices ordenados por similitud
        top_indices = similarities.argsort()[-top_k*2:][::-1]  # Obtener más para filtrar
        
        results = []
        subject_boost = 0.2  # Boost para documentos de la materia detectada
        
        for idx in top_indices:
            if similarities[idx] > 0.05:  # Umbral mínimo de similitud
                doc = self.documents[idx].copy()
                doc['similarity'] = float(similarities[idx])
                
                # Boost si coincide la materia
                if doc['subject'] == subject:
                    doc['similarity'] += subject_boost
                
                results.append(doc)
        
        # Reordenar por similitud ajustada y limitar resultados
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def get_subjects_summary(self) -> Dict:
        """Obtener resumen de materias disponibles"""
        summary = {}
        for subject, entries in self.knowledge_data.items():
            summary[subject] = {
                'name': subject.title(),
                'topics_count': len(entries),
                'topics': [entry['topic'] for entry in entries]
            }
        return summary
    
    def get_available_subjects(self) -> List[str]:
        """Obtener lista de materias disponibles"""
        return list(self.knowledge_data.keys())
    
    def get_topic_by_id(self, topic_id: int) -> Dict:
        """Obtener tema específico por ID"""
        for subject, entries in self.knowledge_data.items():
            for entry in entries:
                if entry['id'] == topic_id:
                    return {
                        'subject': subject,
                        **entry
                    }
        return None
    
    def search_by_subject(self, subject: str) -> List[Dict]:
        """Buscar todos los temas de una materia específica"""
        if subject in self.knowledge_data:
            return [
                {
                    'subject': subject,
                    **entry
                } for entry in self.knowledge_data[subject]
            ]
        return []