import os
from dotenv import find_dotenv, load_dotenv

path = find_dotenv()

load_dotenv(path)

SECRET_KEY = os.getenv("SECRET_KEY")