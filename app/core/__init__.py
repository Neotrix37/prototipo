"""
Módulo core contendo configurações e utilitários principais do sistema.
"""

from .config import settings, get_settings
from . import security

__all__ = ["settings", "get_settings", "security"]
