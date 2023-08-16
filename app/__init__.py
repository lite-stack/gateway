import sys
import os

from .main import app

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir.replace('app', ''))
