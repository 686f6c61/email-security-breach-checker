"""
Email Security Breach Checker v2.0 - Sistema de Caché

Autor: 686f6c61
Repositorio: https://github.com/686f6c61/email-security-breach-checker
Versión: 2.0
Fecha: 2025-11-20
Descripción: Módulo que proporciona funcionalidad de caché para evitar 
llamadas repetitivas a la API y mejorar el rendimiento.

Dirigido a: Comunidad de desarrolladores y profesionales de seguridad
Idioma: Español
Licencia: MIT
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

from .exceptions import CacheError
from config.settings import settings


class CacheManager:
    """Gestiona el caché de respuestas de API para evitar llamadas repetidas."""
    
    def __init__(self, cache_file: Optional[Path] = None):
        """
        Initialize cache manager.
        
        Args:
            cache_file: Path to cache file. If None, uses default location.
        """
        if cache_file is None:
            cache_dir = settings.base_dir / "cache"
            cache_dir.mkdir(exist_ok=True)
            cache_file = cache_dir / "breach_cache.json"
        
        self.cache_file = cache_file
        self.cache_data: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 24 * 60 * 60  # 24 hours in seconds
        
        self._load_cache()
    
    def _load_cache(self) -> None:
        """Load cache data from file."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise CacheError(f"Failed to load cache: {str(e)}")
    
    def _save_cache(self) -> None:
        """Save cache data to file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, indent=2)
        except IOError as e:
            raise CacheError(f"Failed to save cache: {str(e)}")
    
    def _is_cache_valid(self, email: str) -> bool:
        """Check if cached data for email is still valid."""
        if email not in self.cache_data:
            return False
        
        cache_time = self.cache_data[email].get('timestamp', 0)
        current_time = time.time()
        
        return (current_time - cache_time) < self.cache_ttl
    
    def get(self, email: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached breach data for email.
        
        Args:
            email: Email address to get cache for
            
        Returns:
            List of breach data if valid cache exists, None otherwise
        """
        if not self._is_cache_valid(email):
            return None
        
        return self.cache_data[email].get('breaches')
    
    def set(self, email: str, breaches: List[Dict[str, Any]]) -> None:
        """
        Cache breach data for email.
        
        Args:
            email: Email address to cache
            breaches: List of breach data to cache
        """
        self.cache_data[email] = {
            'breaches': breaches,
            'timestamp': time.time()
        }
        
        self._save_cache()
    
    def invalidate(self, email: str) -> None:
        """
        Invalidate cache for specific email.
        
        Args:
            email: Email address to invalidate cache for
        """
        if email in self.cache_data:
            del self.cache_data[email]
            self._save_cache()
    
    def clear_all(self) -> None:
        """Clear all cached data."""
        self.cache_data.clear()
        self._save_cache()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        current_time = time.time()
        valid_entries = 0
        expired_entries = 0
        
        for email, data in self.cache_data.items():
            cache_time = data.get('timestamp', 0)
            if (current_time - cache_time) < self.cache_ttl:
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            'total_entries': len(self.cache_data),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'cache_file': str(self.cache_file),
            'ttl_hours': self.cache_ttl / 3600
        }


# Global cache instance
cache_manager = CacheManager()