import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

class IdeaOpportunity(BaseModel):
    title: str = Field(description="A short, catchy title for the idea.")
    problem: str = Field(description="The core problem being solved.")
    solution: str = Field(description="The proposed solution.")
    sentiment_score: int = Field(description="A score from 1 to 10 indicating the user enthusiasm or pain point intensity based on sentiment.")
    target_audience: str = Field(description="The target audience for this product.")

def fetch_reddit_posts(subreddit="AppIdeas", limit=10):
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    headers = {"User-Agent": "MarketScoutBot/1.0 (Python script)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        posts = []
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            title = post.get("title", "")
            selftext = post.get("selftext", "")
            if title or selftext:
                posts.append({"title": title, "content": selftext})
        return posts
    except Exception as e:
        print(f"Failed to fetch Reddit data: {e}")
        print("Falling back to mock data...")
        return [
            {"title": "App for dog walking in AR", "content": "I want an app that lets me walk virtual dogs in AR while walking in the park."},
            {"title": "Automated meal planner based on fridge photos", "content": "Snap a photo of the fridge and get a weekly meal plan."}
        ]

def analyze_idea_with_langchain(post_text: str):
    if not os.getenv("OPENAI_API_KEY"):
        print("No OPENAI_API_KEY found, returning mock idea.")
        return IdeaOpportunity(
            title="Mock Idea",
            problem="Users are bored while walking.",
            solution="Walk virtual dogs in AR.",
            sentiment_score=8,
            target_audience="Dog lovers and AR enthusiasts."
        )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    parser = PydanticOutputParser(pydantic_object=IdeaOpportunity)
    
    prompt = PromptTemplate(
        template="Analyze the following post which proposes an app or business idea. Extract the key details and perform sentiment analysis to score the market pain point/enthusiasm.\n\nPost:\n{post}\n\n{format_instructions}\n",
        input_variables=["post"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    chain = prompt | llm | parser
    try:
        result = chain.invoke({"post": post_text})
        return result
    except Exception as e:
        print(f"Error parsing idea: {e}")
        return None

def append_to_opportunities(idea: IdeaOpportunity):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, "AI-COMPANY", "OPPORTUNITIES.md")
    
    entry = f"\n## {idea.title}\n"
    entry += f"- **Date Discovered:** {datetime.now().strftime('%Y-%m-%d')}\n"
    entry += f"- **Problem:** {idea.problem}\n"
    entry += f"- **Solution:** {idea.solution}\n"
    entry += f"- **Target Audience:** {idea.target_audience}\n"
    entry += f"- **Sentiment/Pain Score:** {idea.sentiment_score}/10\n"
    
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        print(f"Failed to write to file: {e}")

def main():
    print("Scouting for ideas on Reddit...")
    posts = fetch_reddit_posts(subreddit="AppIdeas", limit=3)
    
    if not posts:
        print("No posts found. Exiting.")
        return

    for post in posts:
        post_text = f"Title: {post['title']}\n\n{post['content']}"
        print(f"Analyzing: {post['title']}")
        idea = analyze_idea_with_langchain(post_text)
        if idea:
            if idea.sentiment_score >= 0: # We'll just write whatever for testing
                append_to_opportunities(idea)
                print(f"Saved opportunity: {idea.title}")
            else:
                print(f"Skipped {idea.title} (Score too low: {idea.sentiment_score})")

if __name__ == "__main__":
    main()
