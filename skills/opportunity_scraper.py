import requests

def scrape_reddit_forhire(keywords):
    """
    A basic web scraper looking at the r/forhire subreddit for job postings
    matching specific keywords. 
    """
    print("--- Jarvis Opportunity Scraper Initializing ---\n")
    print(f"Looking for gigs mentioning: {', '.join(keywords)}")
    
    url = "https://www.reddit.com/r/forhire/new.json?limit=25"
    headers = {'User-Agent': 'Jarvis_Opportunity_Scraper_v1.0'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return
            
        data = response.json()
        posts = data['data']['children']
        
        found_opportunities = []
        
        for post in posts:
            title = post['data']['title']
            url = post['data']['url']
            text = post['data']['selftext'].lower()
            
            if "[hiring]" in title.lower():
                if any(keyword.lower() in text or keyword.lower() in title.lower() for keyword in keywords):
                    found_opportunities.append({"title": title, "link": url})
                    
        print(f"\nFound {len(found_opportunities)} potential leads:")
        for opp in found_opportunities:
            print(f"- {opp['title']}")
            print(f"  Link: {opp['link']}\n")
            
    except Exception as e:
        print(f"Scraping error: {e}")

if __name__ == "__main__":
    my_skills = ['python', 'automation', 'scraping', 'AI', 'bot']
    scrape_reddit_forhire(my_skills)
