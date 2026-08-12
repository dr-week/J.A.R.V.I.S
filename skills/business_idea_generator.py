import requests
import os
from dotenv import load_dotenv

# Load env variables from .env file if it exists
load_dotenv()

NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "YOUR_NEWSAPI_KEY_HERE")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_KEY_HERE")

def fetch_and_filter_news(query="technology OR business OR startup"):
    """Connects to NewsAPI, fetches top headlines, and filters them."""
    print(f"--- Fetching latest news for: {query} ---")
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&pageSize=10&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"NewsAPI Error: Please check your API key. (Status: {response.status_code})")
            return []
            
        articles = response.json().get('articles', [])
        
        filtered_headlines = []
        for article in articles:
            title = article.get('title')
            desc = article.get('description')
            if title and desc:
                filtered_headlines.append(f"{title} - {desc}")
                
        return filtered_headlines
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def generate_business_ideas(headlines):
    """Generates business ideas based on headlines using OpenAI."""
    if not headlines:
        print("No headlines found to analyze.")
        return

    print(f"\n--- Analyzing {len(headlines)} headlines and generating business ideas ---")
    news_context = "\n".join(headlines[:5])
    
    prompt = f"""
    You are an expert startup founder and business strategist. 
    Analyze the following recent news headlines:
    
    {news_context}
    
    Based ONLY on these current events and trends, generate 3 highly actionable, 
    low-capital business ideas or software automation ideas that could be built right now 
    to capitalize on these trends. Format as a numbered list with a brief explanation.
    """

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a business strategist AI."},
                {"role": "user", "content": prompt}
            ]
        )
        
        ideas = response.choices[0].message.content
        print("\n💡 JARVIS BUSINESS IDEA GENERATOR 💡\n")
        print(ideas)
        
    except ImportError:
        print("Error: Please 'pip install openai' to run the idea generator.")
    except Exception as e:
        print(f"LLM API Error (Did you set your API key?): {e}")

if __name__ == "__main__":
    print("Initializing Jarvis Idea Generator...\n")
    recent_news = fetch_and_filter_news(query="AI OR automation OR software")
    if recent_news:
        generate_business_ideas(recent_news)
