import re
from typing import List, Dict
import html

class SecurityManager:
    def __init__(self):
        self.inappropriate_words = self.load_inappropriate_words()
        self.max_question_length = 500
        self.min_question_length = 3
        
    def load_inappropriate_words(self) -> List[str]:
        """Cargar lista de palabras inapropiadas"""
        # Lista básica de palabras a filtrar (expandible)
        return [
            'spam', 'hack', 'virus', 'malware',
            # Agregar más palabras según necesidades específicas
        ]
    
    def validate_question(self, question: str) -> bool:
        """Validar que la pregunta sea apropiada y segura"""
        if not question or not isinstance(question, str):
            return False
        
        # Verificar longitud
        if len(question) < self.min_question_length or len(question) > self.max_question_length:
            return False
        
        # Limpiar y normalizar
        clean_question = question.lower().strip()
        
        # Verificar contenido inapropiado
        for word in self.inappropriate_words:
            if word in clean_question:
                return False
        
        # Verificar patrones sospechosos
        if self.contains_suspicious_patterns(clean_question):
            return False
        
        # Verificar que no sea solo caracteres especiales
        if not re.search(r'[a-záéíóúñü]', clean_question):
            return False
        
        return True
    
    def contains_suspicious_patterns(self, text: str) -> bool:
        """Detectar patrones sospechosos en el texto"""
        suspicious_patterns = [
            r'<script.*?>',  # Scripts
            r'javascript:',  # JavaScript
            r'<.*?>',        # Tags HTML
            r'sql.*injection',  # SQL injection
            r'union.*select',   # SQL injection
            r'drop.*table',     # SQL injection
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def sanitize_input(self, text: str) -> str:
        """Sanitizar entrada del usuario"""
        if not text:
            return ""
        
        # Escapar HTML
        sanitized = html.escape(text)
        
        # Remover caracteres de control
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
        
        # Normalizar espacios
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        return sanitized
    
    def validate_input(self, text: str) -> bool:
        """Validación general de entrada"""
        if not text or not isinstance(text, str):
            return False
        
        # Verificar longitud razonable
        if len(text) > 1000:
            return False
        
        # Verificar que no sea solo espacios
        if not text.strip():
            return False
        
        return True
    
    def validate_email(self, email: str) -> bool:
        """Validar formato de email"""
        if not email or not isinstance(email, str):
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    def rate_limit_check(self, session_id: str, max_requests: int = 60, 
                        time_window: int = 3600) -> bool:
        """Verificar límite de velocidad (rate limiting)"""
        # Implementación básica - en producción usar Redis o similar
        # Por ahora retorna True (sin límite)
        return True
    
    def log_security_event(self, event_type: str, details: Dict):
        """Registrar evento de seguridad"""
        # En producción, esto debería escribir a un log seguro
        print(f"Security Event: {event_type} - {details}")
    
    def check_content_safety(self, content: str) -> Dict:
        """Verificar seguridad del contenido"""
        result = {
            'is_safe': True,
            'issues': [],
            'confidence': 1.0
        }
        
        if not self.validate_question(content):
            result['is_safe'] = False
            result['issues'].append('Contenido inapropiado detectado')
            result['confidence'] = 0.0
        
        if self.contains_suspicious_patterns(content):
            result['is_safe'] = False
            result['issues'].append('Patrones sospechosos detectados')
            result['confidence'] = 0.0
        
        return result