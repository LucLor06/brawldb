import os
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(current_dir, '.env')
load_dotenv(path)

DJANGO_SECRET_KEY = os.getenv("BRAWLDATABASE_SECRET_KEY")