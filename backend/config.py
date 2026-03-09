import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    JINA_API_KEY = os.getenv("JINA_API_KEY", "")
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

config = Config()
