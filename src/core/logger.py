"""
Configuration du logging et utilitaires d'affichage
"""

import io
import os
import sys


def setup_utf8_encoding():
    """Configure l'encodage UTF-8 pour Windows"""
    if sys.platform == "win32":
        # Configurer l'encodage UTF-8 pour la console
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
            )
        if hasattr(sys.stderr, "buffer"):
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True
            )

        # Forcer l'encodage UTF-8 dans l'environnement
        os.environ["PYTHONIOENCODING"] = "utf-8"


def log_print(*args, **kwargs):
    """Affiche un message avec flush automatique pour garantir la visibilité"""
    kwargs.setdefault("flush", True)
    print(*args, **kwargs)
