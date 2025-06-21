import random
from typing import Dict, List
import re

class ResponseGenerator:
    def __init__(self):
        self.response_templates = self.load_response_templates()
        self.educational_phrases = self.load_educational_phrases()
        
    def load_response_templates(self) -> Dict:
        """Cargar plantillas de respuesta por tipo de pregunta"""
        return {
            'definition': [
                "Te explico qué es {topic}: {content}",
                "El concepto de {topic} se refiere a: {content}",
                "{topic} se define como: {content}"
            ],
            'explanation': [
                "Te explico cómo funciona {topic}: {content}",
                "Para entender {topic}, es importante saber que: {content}",
                "El proceso de {topic} funciona así: {content}"
            ],
            'calculation': [
                "Para resolver este tipo de problema sobre {topic}: {content}",
                "Los pasos para calcular {topic} son: {content}",
                "Te ayudo con el cálculo de {topic}: {content}"
            ],
            'comparison': [
                "La diferencia entre estos conceptos de {topic} es: {content}",
                "Comparando estos elementos de {topic}: {content}",
                "Para distinguir entre estos conceptos de {topic}: {content}"
            ],
            'example': [
                "Aquí tienes un ejemplo de {topic}: {content}",
                "Para ilustrar {topic}, considera esto: {content}",
                "Un caso práctico de {topic} sería: {content}"
            ],
            'general': [
                "Sobre {topic}: {content}",
                "En relación a {topic}: {content}",
                "Respecto a {topic}: {content}"
            ]
        }
    
    def load_educational_phrases(self) -> Dict:
        """Cargar frases educativas motivacionales"""
        return {
            'encouragement': [
                "¡Excelente pregunta!",
                "Me alegra que preguntes sobre esto.",
                "Es muy bueno que tengas curiosidad por este tema.",
                "Esa es una pregunta muy inteligente."
            ],
            'learning_tips': [
                "💡 Consejo: Practica con ejercicios similares para reforzar este concepto.",
                "📚 Tip de estudio: Haz un resumen de los puntos clave.",
                "🎯 Recomendación: Relaciona este tema con ejemplos de la vida real.",
                "✨ Sugerencia: Explica este concepto a alguien más para consolidar tu aprendizaje."
            ],
            'follow_up': [
                "¿Te gustaría que profundice en algún aspecto específico?",
                "¿Hay algo más sobre este tema que te interese saber?",
                "¿Necesitas ejemplos adicionales o ejercicios prácticos?",
                "¿Te quedó claro o prefieres que lo explique de otra manera?"
            ]
        }
    
    def generate_response(self, original_question: str, processed_question: Dict, 
                         relevant_content: List[Dict]) -> Dict:
        """Generar respuesta completa basada en la pregunta y contenido relevante"""
        
        if not relevant_content:
            return self.generate_fallback_response(processed_question)
        
        # Seleccionar el contenido más relevante
        best_match = relevant_content[0]
        subject = best_match['subject']
        topic = best_match['topic']
        content = best_match['content']
        confidence = best_match['similarity']
        
        # Seleccionar plantilla según tipo de pregunta
        question_type = processed_question.get('question_type', 'general')
        templates = self.response_templates.get(question_type, self.response_templates['general'])
        template = random.choice(templates)
        
        # Generar respuesta principal
        main_response = template.format(topic=topic, content=content)
        
        # Agregar elementos educativos
        encouragement = random.choice(self.educational_phrases['encouragement'])
        learning_tip = random.choice(self.educational_phrases['learning_tips'])
        follow_up = random.choice(self.educational_phrases['follow_up'])
        
        # Construir respuesta completa
        full_response = f"{encouragement}\n\n{main_response}\n\n{learning_tip}\n\n{follow_up}"
        
        # Generar sugerencias relacionadas
        suggestions = self.generate_suggestions(subject, topic, relevant_content)
        
        # Generar recursos adicionales
        resources = self.generate_resources(subject, topic)
        
        return {
            'response': full_response,
            'subject': subject,
            'topic': topic,
            'confidence': confidence,
            'suggestions': suggestions,
            'resources': resources,
            'question_type': question_type
        }
    
    def generate_fallback_response(self, processed_question: Dict) -> Dict:
        """Generar respuesta cuando no se encuentra contenido relevante"""
        subject = processed_question.get('subject', 'general')
        
        fallback_responses = [
            "Disculpa, no tengo información específica sobre esa consulta en mi base de conocimiento actual.",
            "Esa es una pregunta interesante, pero necesito más información específica para ayudarte mejor.",
            "No encuentro contenido específico para tu pregunta, pero puedo ayudarte con temas relacionados.",
        ]
        
        response = random.choice(fallback_responses)
        
        # Sugerir temas relacionados si se detectó una materia
        if subject != 'general':
            response += f"\n\n¿Te interesa que te hable sobre otros temas de {subject}?"
        
        response += "\n\n💡 Consejo: Intenta reformular tu pregunta o ser más específico sobre el tema que te interesa."
        response += "\n\n¿Puedes darme más detalles sobre lo que necesitas saber?"
        
        return {
            'response': response,
            'subject': subject,
            'topic': 'consulta_general',
            'confidence': 0.1,
            'suggestions': self.get_general_suggestions(subject),
            'resources': [],
            'question_type': 'general'
        }
    
    def generate_suggestions(self, subject: str, current_topic: str, 
                           relevant_content: List[Dict]) -> List[str]:
        """Generar sugerencias de temas relacionados"""
        suggestions = []
        
        # Sugerencias basadas en contenido relevante
        for content in relevant_content[1:4]:  # Tomar hasta 3 temas relacionados
            if content['topic'] != current_topic:
                suggestions.append(f"¿Qué es {content['topic']}?")
        
        # Sugerencias específicas por materia
        subject_suggestions = {
            'matematicas': [
                "¿Cómo resolver ecuaciones cuadráticas?",
                "¿Qué son las funciones lineales?",
                "¿Cómo calcular el área de figuras geométricas?",
                "¿Qué es la trigonometría básica?"
            ],
            'fisica': [
                "¿Cómo calcular la velocidad y aceleración?",
                "¿Qué son las ondas y el sonido?",
                "¿Cómo funciona la electricidad?",
                "¿Qué es la energía y sus transformaciones?"
            ],
            'quimica': [
                "¿Cómo balancear ecuaciones químicas?",
                "¿Qué son los ácidos y bases?",
                "¿Cómo funciona la estructura atómica?",
                "¿Qué son las reacciones químicas?"
            ],
            'biologia': [
                "¿Cómo funciona la respiración celular?",
                "¿Qué es la genética básica?",
                "¿Cómo funcionan los ecosistemas?",
                "¿Qué es la evolución?"
            ]
        }
        
        if subject in subject_suggestions:
            suggestions.extend(random.sample(subject_suggestions[subject], 2))
        
        return suggestions[:5]  # Máximo 5 sugerencias
    
    def get_general_suggestions(self, subject: str) -> List[str]:
        """Obtener sugerencias generales por materia"""
        general_suggestions = {
            'matematicas': [
                "¿Cómo resolver ecuaciones lineales?",
                "¿Qué es el teorema de Pitágoras?",
                "¿Cómo graficar funciones?"
            ],
            'fisica': [
                "¿Cuáles son las leyes de Newton?",
                "¿Qué es la energía cinética?",
                "¿Cómo funciona la gravedad?"
            ],
            'quimica': [
                "¿Cómo está organizada la tabla periódica?",
                "¿Qué son los enlaces químicos?",
                "¿Cómo se forman los compuestos?"
            ],
            'biologia': [
                "¿Qué es una célula?",
                "¿Cómo funciona la fotosíntesis?",
                "¿Qué es el ADN?"
            ],
            'general': [
                "¿Sobre qué materia te gustaría aprender?",
                "¿Necesitas ayuda con matemáticas, física, química o biología?",
                "¿Qué tema específico te interesa?"
            ]
        }
        
        return general_suggestions.get(subject, general_suggestions['general'])
    
    def generate_resources(self, subject: str, topic: str) -> List[Dict]:
        """Generar recursos educativos adicionales"""
        resources = []
        
        # Recursos por materia
        subject_resources = {
            'matematicas': [
                {
                    'type': 'video',
                    'title': 'Khan Academy - Matemáticas',
                    'description': 'Videos explicativos paso a paso',
                    'url': 'https://es.khanacademy.org/math'
                },
                {
                    'type': 'ejercicios',
                    'title': 'Ejercicios de práctica',
                    'description': 'Problemas resueltos y propuestos',
                    'url': '#'
                }
            ],
            'fisica': [
                {
                    'type': 'simulacion',
                    'title': 'PhET Simulaciones',
                    'description': 'Simulaciones interactivas de física',
                    'url': 'https://phet.colorado.edu/es/'
                }
            ],
            'quimica': [
                {
                    'type': 'tabla',
                    'title': 'Tabla Periódica Interactiva',
                    'description': 'Explora los elementos químicos',
                    'url': '#'
                }
            ],
            'biologia': [
                {
                    'type': 'diagrama',
                    'title': 'Atlas de Biología',
                    'description': 'Diagramas y esquemas biológicos',
                    'url': '#'
                }
            ]
        }
        
        if subject in subject_resources:
            resources = subject_resources[subject]
        
        return resources
    
    def adjust_response_level(self, response: str, difficulty_level: str) -> str:
        """Ajustar el nivel de la respuesta según la dificultad"""
        if difficulty_level == 'basic':
            # Simplificar lenguaje
            response = response.replace('establecer', 'decir')
            response = response.replace('determinar', 'encontrar')
            response = response.replace('constituir', 'formar')
        elif difficulty_level == 'advanced':
            # Agregar más detalles técnicos
            response += "\n\n🔬 Nota avanzada: Este concepto se relaciona con principios más complejos que puedes explorar en niveles superiores."
        
        return response