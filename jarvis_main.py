import os
from dotenv import load_dotenv
from skills.market_scanner import scan_market
from skills.opportunity_scraper import scrape_reddit_forhire
from skills.business_idea_generator import fetch_and_filter_news, generate_business_ideas
from tools.money_maker.intelligence.freebies_and_deals import scan_all_freebies_and_deals, print_summary
from tools.money_maker.probability.expected_value import mm_calculate_expected_value
from tools.money_maker.finance.arbitrage import mm_detect_arbitrage_spread
from tools.money_maker.probability.monte_carlo import mm_monte_carlo_sim

def main_menu():
    print("\n===================================")
    print("      JARVIS MONEY MAKER AI")
    print("===================================")
    print("1. Run Market Scanner")
    print("2. Run Opportunity Scraper (Gigs/Leads)")
    print("3. Run Business Idea Generator")
    print("4. Scan Free Stuff, Deals & Easy Money Offers")
    print("5. Calculate Expected Value (EV) & Edge")
    print("6. Detect Cross-Market Arbitrage Spread")
    print("7. Run Monte Carlo Portfolio Risk Simulation")
    print("8. Exit")
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
            report = scan_all_freebies_and_deals()
            print_summary(report)

        elif choice == '5':
            win_p = float(input("Enter Win Probability % (e.g. 60): ") or 60)
            gain = float(input("Enter Potential Gain in ₹/$ (e.g. 5000): ") or 5000)
            loss_p = 100 - win_p
            loss = float(input("Enter Potential Loss in ₹/$ (e.g. 1500): ") or 1500)
            res = mm_calculate_expected_value(win_p, gain, loss_p, loss)
            print("\n" + "=" * 40)
            print(f"Expected Value (EV): {res['expected_value']}")
            print(f"Risk / Reward Ratio: {res['risk_reward_ratio']}")
            print(f"Verdict: {res['recommendation']}")
            print("=" * 40)

        elif choice == '6':
            asset = input("Asset Name (e.g. BTC, Gold): ") or "BTC"
            p_a = float(input("Price on Exchange A: ") or 60000)
            p_b = float(input("Price on Exchange B: ") or 61200)
            res = mm_detect_arbitrage_spread(asset, p_a, "Exchange A", p_b, "Exchange B")
            print("\n" + "=" * 40)
            print(f"Arbitrage Net Profit: {res['net_profit_per_unit']} ({res['net_profit_pct']}%)")
            print(f"Action: Buy from {res['buy_from']} -> Sell on {res['sell_to']}")
            print(f"Opportunity Detected: {res['is_opportunity']}")
            print("=" * 40)

        elif choice == '7':
            cap = float(input("Initial Capital in ₹/$ (e.g. 50000): ") or 50000)
            res = mm_monte_carlo_sim(cap, 0.6, 2.0)
            print("\n" + "=" * 40)
            print(f"Expected Final Balance: {res['expected_final_capital']}")
            print(f"Profit Probability: {res['profit_probability_pct']}%")
            print(f"Risk of Ruin: {res['risk_of_ruin_pct']}%")
            print(f"System Recommendation: {res['recommendation']}")
            print("=" * 40)

        elif choice == '8':
            print("Shutting down Jarvis. Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
