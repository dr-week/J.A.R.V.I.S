import os
from dotenv import load_dotenv
from skills.market_scanner import scan_market
from skills.opportunity_scraper import scrape_reddit_forhire
from skills.business_idea_generator import fetch_and_filter_news, generate_business_ideas

def main_menu():
    print("\n===================================")
    print("      JARVIS MONEY MAKER AI")
    print("===================================")
    print("1. Run Market Scanner")
    print("2. Run Opportunity Scraper (Gigs/Leads)")
    print("3. Run Business Idea Generator")
    print("4. Exit")
    print("===================================")
    
    choice = input("Select an action: ")
    return choice

def main():
    # Load environment variables
    load_dotenv()
    
    while True:
        choice = main_menu()
        
        if choice == '1':
            watchlist = ['AAPL', 'MSFT', 'GOOGL', 'BTC-USD']
            scan_market(watchlist)
        
        elif choice == '2':
            skills = ['python', 'automation', 'scraping', 'AI']
            scrape_reddit_forhire(skills)
            
        elif choice == '3':
            recent_news = fetch_and_filter_news(query="AI OR automation OR software")
            if recent_news:
                generate_business_ideas(recent_news)
                
        elif choice == '4':
            print("Shutting down Jarvis. Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
