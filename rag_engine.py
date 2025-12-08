import os
import google.generativeai as genai
from pypdf import PdfReader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    # Fallback for Streamlit Cloud or if .env is missing, though user should set it.
    # We will handle this gracefully in the app.
    print("WARNING: GEMINI_API_KEY not found in environment variables.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

def load_knowledge_base(data_dir="gov_data"):
    """
    Reads all PDFs in the specified directory and returns their combined text.
    """
    knowledge_text = ""
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")
        return ""

    files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]
    
    if not files:
        print(f"No PDF files found in {data_dir}")
        return ""

    print(f"Loading {len(files)} PDFs from {data_dir}...")
    
    for file in files:
        file_path = os.path.join(data_dir, file)
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            knowledge_text += f"\n--- START OF DOCUMENT: {file} ---\n{text}\n--- END OF DOCUMENT ---\n"
            print(f"Loaded: {file}")
        except Exception as e:
            print(f"Error reading {file}: {e}")
            
    return knowledge_text

# Load knowledge base once at startup
print("Initializing Knowledge Base...")
KNOWLEDGE_BASE_CACHE = load_knowledge_base()
print("Knowledge Base Loaded.")

def get_ai_response(user_query, news_alert=None):
    """
    Generates a response using Gemini 1.5 Flash.
    Context includes the loaded PDFs and any active news alert.
    """
    
    # Load the knowledge base (in a real app, this should be cached/indexed)
    # CACHED: We load this once at startup now.
    knowledge_context = KNOWLEDGE_BASE_CACHE
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    system_prompt = """You are Swasthya Sathi, a helpful health companion for rural Odisha.
    
INSTRUCTIONS:
1. If 'news_alert' is provided and is not None, YOU MUST START your response with a WARNING based on that alert.
2. Answer the 'user_query' using ONLY the provided 'knowledge_context'. Do not hallucinate facts not in the context.
3. If the answer is not in the context, say "I do not have official government information on this topic yet."
4. Translate your answer to the language of the user's query (English, Hindi, or Odia). Detect the language from the query.
5. Keep the response SHORT and CONCISE (under 160 characters if possible, max 3 sentences) as it may be sent via SMS/WhatsApp.
"""

    prompt = f"""
{system_prompt}

--- KNOWLEDGE BASE ---
{knowledge_context}
--- END KNOWLEDGE BASE ---

--- REAL-TIME NEWS ALERT ---
{news_alert if news_alert else "No active alerts."}
--- END NEWS ALERT ---

USER QUERY: {user_query}
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating response: {e}"

if __name__ == "__main__":
    # Test the function
    # Create a dummy PDF for testing if none exists
    if not os.path.exists("gov_data/test.pdf"):
        pass # We can't easily create a PDF here without reportlab, skipping.
        
    print("Testing AI Response...")
    # Note: This will fail if no API key is set or no PDFs are present, but that's expected.
    # print(get_ai_response("What are the symptoms of Dengue?", "Dengue Outbreak in Cuttack"))
