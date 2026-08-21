"""Free Opportunities, Deals & Promo Scanner for Jarvis Money Maker.

Aggregates multiple public RSS & JSON feeds with automatic fallbacks to discover:
- Freebies, Giveaways, and Digital Credits (Cloud credits, free software, dev tools)
- High-value Sign-up bonuses & Referral rewards
- Zero-cost micro-earning / bounty opportunities & tech deals
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Reliable public RSS & Feed sources for global & India-specific deals & opportunities
SOURCES = [
    {
        "name": "DesiDime Deals (Top India Deals & Freebies)",
        "url": "https://www.desidime.com/deals/popular.rss",
        "type": "rss",
        "category": "India Loot & Deals"
    },
    {
        "name": "Reddit r/IndiaInvestments (India Financial Insights)",
        "url": "https://www.reddit.com/r/IndiaInvestments/new/.rss",
        "type": "rss",
        "category": "India Investment & Wealth"
    },
    {
        "name": "Reddit r/IndianStreetBets (Trading Opportunities)",
        "url": "https://www.reddit.com/r/IndianStreetBets/new/.rss",
        "type": "rss",
        "category": "India Market Opportunities"
    },
    {
        "name": "Reddit r/Freebies (Global Physical & Digital Free Stuff)",
        "url": "https://www.reddit.com/r/freebies/new/.rss",
        "type": "rss",
        "category": "Freebies & Giveaways"
    },
    {
        "name": "Reddit r/Deals (Global Discounts & Pricing Errors)",
        "url": "https://www.reddit.com/r/deals/new/.rss",
        "type": "rss",
        "category": "Deals & Discounts"
    },
    {
        "name": "Reddit r/BeerMoney (Online Side Gigs & Micro-Tasks)",
        "url": "https://www.reddit.com/r/beermoney/new/.rss",
        "type": "rss",
        "category": "Online Micro-Earning & Bounties"
    },
    {
        "name": "Hacker News (Tech Credits & Grants)",
        "url": "https://hnrss.org/newest?q=free+OR+giveaway+OR+credit+OR+bonus",
        "type": "rss",
        "category": "Tech Credits & Free Dev Tools"
    }
]

HIGH_VALUE_KEYWORDS = [
    "free", "100% off", "bonus", "₹", "inr", "rs.", "rs ", "cashback", "loot", "coupon",
    "upi", "cred", "discount", "offer", "airdrop", "bounty", "gift card", "voucher",
    "zero brokerage", "arbitrage", "dividend", "yield", "credit", "grant"
]

def parse_rss_feed(source_config: Dict[str, str]) -> List[Dict[str, Any]]:
    """Fetches and parses RSS/Atom XML feeds reliably."""
    results = []
    try:
        response = requests.get(source_config["url"], headers=HEADERS, timeout=12)
        if response.status_code != 200:
            return []
        
        root = ET.fromstring(response.content)
        
        # Handle standard RSS <item> vs Atom <entry>
        items = root.findall(".//item")
        if not items:
            # Check for Atom format (xmlns default)
            items = root.findall(".//{http://www.w3.org/2005/Atom}entry")
            
        for item in items[:15]:
            title_node = item.find("title")
            if title_node is None:
                title_node = item.find("{http://www.w3.org/2005/Atom}title")
            title = title_node.text.strip() if (title_node is not None and title_node.text) else "Untitled Offer"
            
            link_node = item.find("link")
            if link_node is None:
                link_node = item.find("{http://www.w3.org/2005/Atom}link")
                
            if link_node is not None:
                link = link_node.text or link_node.attrib.get("href", "")
            else:
                link = ""
                
            keyword_matches = [kw for kw in HIGH_VALUE_KEYWORDS if kw in title.lower()]
            relevance_score = len(keyword_matches) * 10
            
            results.append({
                "title": title,
                "link": link,
                "category": source_config["category"],
                "source": source_config["name"],
                "keywords_matched": keyword_matches,
                "relevance_score": relevance_score
            })
            
    except Exception as e:
        pass
    return results

def scan_all_freebies_and_deals() -> Dict[str, Any]:
    """Runs a full scan across all targets and returns organized results."""
    all_opportunities = []
    
    print("=" * 60)
    print("[*] JARVIS MONEY MAKER: FREE OPPORTUNITIES & DEALS SCANNER")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    for source in SOURCES:
        print(f"[*] Scanning {source['name']}...")
        opps = parse_rss_feed(source)
        all_opportunities.extend(opps)
    
    # Sort opportunities by relevance score
    sorted_opps = sorted(all_opportunities, key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    # Categorize items
    categories: Dict[str, List[Dict[str, Any]]] = {}
    for opp in sorted_opps:
        cat = opp.get("category", "General")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(opp)
        
    return {
        "scan_time": datetime.now().isoformat(),
        "total_found": len(all_opportunities),
        "categorized": categories,
        "top_picks": sorted_opps[:10]
    }

def print_summary(report: Dict[str, Any]):
    """Pretty prints the scan report in the terminal."""
    if not report["top_picks"]:
        print("\n[!] No active deals found on this pass. Check internet connection.")
        return

    print("\n" + "#" * 60)
    print(">>> TOP 10 HIGH-VALUE PICKS (Highest Relevance)")
    print("#" * 60)
    
    for idx, item in enumerate(report["top_picks"], 1):
        print(f"\n[{idx}] {item['title']}")
        print(f"    Category: {item['category']}")
        print(f"    Link: {item['link']}")
        if item.get('keywords_matched'):
            print(f"    Tags: {', '.join(item['keywords_matched'])}")

    print("\n" + "=" * 60)
    print("SCAN COMPLETED -- OPPORTUNITIES BY CATEGORY")
    print("=" * 60)
    for cat, items in report["categorized"].items():
        print(f"\n--- {cat.upper()} ({len(items)} items found) ---")
        for item in items[:4]:
            print(f"- {item['title'][:85]}...")
            print(f"  URL: {item['link']}")

# Optional registration into Jarvis Hands tool registry if run within Jarvis backend
try:
    from backend.app.hands.registry import register
    register(
        {
            "name": "mm_scan_freebies_and_deals",
            "description": "Scans online feeds for freebies, promo offers, sign-up rewards, and micro-earning gigs.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "scan_time": {"type": "string"},
                    "total_found": {"type": "integer"},
                    "top_picks": {"type": "array", "items": {"type": "object"}},
                    "categorized": {"type": "object"}
                }
            },
            "scopes": [],
            "tags": ["freebies", "deals", "opportunities", "money_maker"],
        },
        scan_all_freebies_and_deals,
    )
except ImportError:
    pass

if __name__ == "__main__":
    report = scan_all_freebies_and_deals()
    print_summary(report)
