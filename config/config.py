import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OR_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"