import os 
from dotenv import load_dotenv
load_dotenv()


class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_FALLBACK_API_KEY = os.getenv("GROQ_FALLBACK_API_KEY")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_URL = os.getenv("QDRANT_CLUSTER_ENDPOINT")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    QDRANT_COLLECTION = "rag_collection"
    GROQ_MODEL = "openai/gpt-oss-120b"
    GEMINI_FALLBACK_API_KEY = os.getenv("GEMINI_FALLBACK_API_KEY")  
    GROQ_SLUG= "rag"
    GROQ_SLUG_2= "rag2"
    PORTKEY_API_KEY=os.getenv("PORTKEY_API_KEY")
    PORTKEY_PRIMARY_CONFIG_ID=os.getenv("PORTKEY_PRIMARY_CONFIG_ID")
settings = Settings()

