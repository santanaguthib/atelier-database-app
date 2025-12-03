"""
Atelier Database Management System - Modules Package
"""

__version__ = '1.0.0'
__author__ = 'Course Project'
__description__ = 'Database Security & Functionality Management'

# Module imports
from . import audit
from . import ddm
from . import extended_events
from . import backup
from . import tde
from . import filegroups
from . import triggers
from . import procedures
from . import views
from . import functions

__all__ = [
    'audit',
    'ddm',
    'extended_events',
    'backup',
    'tde',
    'filegroups',
    'triggers',
    'procedures',
    'views',
    'functions'
]
