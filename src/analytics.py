from datetime import datetime, timedelta
from typing import Dict, List
import json

class Analytics:
    def __init__(self):
        # Almacenamiento en memoria para estadísticas
        self.session_stats = {}
        self.global_stats = {
            'total_questions': 0,
            'subjects_distribution': {},
            'question_types_distribution': {},
            'average_confidence': 0.0,
            'feedback_ratings': [],
            'daily_usage': {},
            'popular_topics': {}
        }
    
    def update_session_stats(self, session_id: str, subject: str):
        """Actualizar estadísticas de sesión"""
        if session_id not in self.session_stats:
            self.session_stats[session_id] = {
                'questions_count': 0,
                'subjects_covered': set(),
                'start_time': datetime.now(),
                'last_activity': datetime.now(),
                'confidence_scores': []
            }
        
        stats = self.session_stats[session_id]
        stats['questions_count'] += 1
        stats['subjects_covered'].add(subject)
        stats['last_activity'] = datetime.now()
        
        # Actualizar estadísticas globales
        self.global_stats['total_questions'] += 1
        
        # Distribución por materias
        if subject not in self.global_stats['subjects_distribution']:
            self.global_stats['subjects_distribution'][subject] = 0
        self.global_stats['subjects_distribution'][subject] += 1
        
        # Uso diario
        today = datetime.now().date().isoformat()
        if today not in self.global_stats['daily_usage']:
            self.global_stats['daily_usage'][today] = 0
        self.global_stats['daily_usage'][today] += 1
    
    def record_feedback(self, session_id: str, rating: int):
        """Registrar feedback del usuario"""
        self.global_stats['feedback_ratings'].append({
            'rating': rating,
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id
        })
        
        # Calcular promedio de feedback
        ratings = [f['rating'] for f in self.global_stats['feedback_ratings']]
        self.global_stats['average_feedback'] = sum(ratings) / len(ratings)
    
    def record_confidence_score(self, session_id: str, confidence: float):
        """Registrar puntuación de confianza"""
        if session_id in self.session_stats:
            self.session_stats[session_id]['confidence_scores'].append(confidence)
        
        # Actualizar promedio global de confianza
        all_scores = []
        for stats in self.session_stats.values():
            all_scores.extend(stats['confidence_scores'])
        
        if all_scores:
            self.global_stats['average_confidence'] = sum(all_scores) / len(all_scores)
    
    def get_session_summary(self, session_id: str) -> Dict:
        """Obtener resumen de la sesión actual"""
        if session_id not in self.session_stats:
            return {}
        
        stats = self.session_stats[session_id]
        session_duration = datetime.now() - stats['start_time']
        
        return {
            'questions_asked': stats['questions_count'],
            'subjects_covered': list(stats['subjects_covered']),
            'session_duration_minutes': int(session_duration.total_seconds() / 60),
            'average_confidence': (
                sum(stats['confidence_scores']) / len(stats['confidence_scores'])
                if stats['confidence_scores'] else 0.0
            ),
            'start_time': stats['start_time'].isoformat(),
            'last_activity': stats['last_activity'].isoformat()
        }
    
    def get_general_stats(self) -> Dict:
        """Obtener estadísticas generales del sistema"""
        # Calcular estadísticas de sesiones activas
        active_sessions = len(self.session_stats)
        total_session_time = 0
        
        for stats in self.session_stats.values():
            session_duration = stats['last_activity'] - stats['start_time']
            total_session_time += session_duration.total_seconds()
        
        avg_session_time = (
            total_session_time / active_sessions / 60
            if active_sessions > 0 else 0
        )
        
        # Top materias
        sorted_subjects = sorted(
            self.global_stats['subjects_distribution'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Estadísticas de los últimos 7 días
        last_week_usage = self.get_last_week_usage()
        
        return {
            'total_questions': self.global_stats['total_questions'],
            'active_sessions': active_sessions,
            'average_session_time_minutes': round(avg_session_time, 1),
            'average_confidence': round(self.global_stats['average_confidence'], 2),
            'average_feedback': round(
                self.global_stats.get('average_feedback', 0), 2
            ),
            'subjects_distribution': dict(sorted_subjects),
            'top_subject': sorted_subjects[0][0] if sorted_subjects else 'N/A',
            'last_week_usage': last_week_usage,
            'total_feedback_count': len(self.global_stats['feedback_ratings'])
        }
    
    def get_last_week_usage(self) -> Dict:
        """Obtener uso de los últimos 7 días"""
        last_week = {}
        today = datetime.now().date()
        
        for i in range(7):
            date = (today - timedelta(days=i)).isoformat()
            last_week[date] = self.global_stats['daily_usage'].get(date, 0)
        
        return last_week
    
    def get_subject_analytics(self, subject: str) -> Dict:
        """Obtener analíticas específicas de una materia"""
        subject_questions = self.global_stats['subjects_distribution'].get(subject, 0)
        total_questions = self.global_stats['total_questions']
        
        percentage = (
            (subject_questions / total_questions * 100)
            if total_questions > 0 else 0
        )
        
        return {
            'subject': subject,
            'questions_count': subject_questions,
            'percentage_of_total': round(percentage, 1),
            'rank': self.get_subject_rank(subject)
        }
    
    def get_subject_rank(self, subject: str) -> int:
        """Obtener ranking de una materia por popularidad"""
        sorted_subjects = sorted(
            self.global_stats['subjects_distribution'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for i, (subj, _) in enumerate(sorted_subjects):
            if subj == subject:
                return i + 1
        
        return len(sorted_subjects) + 1
    
    def export_analytics(self) -> Dict:
        """Exportar todas las analíticas para reportes"""
        return {
            'timestamp': datetime.now().isoformat(),
            'global_stats': self.global_stats,
            'session_count': len(self.session_stats),
            'sessions_summary': {
                session_id: self.get_session_summary(session_id)
                for session_id in self.session_stats.keys()
            }
        }
    
    def reset_analytics(self):
        """Reiniciar todas las estadísticas (para testing o limpieza)"""
        self.session_stats.clear()
        self.global_stats = {
            'total_questions': 0,
            'subjects_distribution': {},
            'question_types_distribution': {},
            'average_confidence': 0.0,
            'feedback_ratings': [],
            'daily_usage': {},
            'popular_topics': {}
        }