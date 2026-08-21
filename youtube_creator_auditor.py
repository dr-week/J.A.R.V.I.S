"""YouTube Creator Outbound Radar & Dynamic Channel Discovery Engine (v2.0).

Features:
1. Dynamic Creator Channel Discovery (searches topics like 'Podcasts India', 'SaaS Growth', 'Tech Reviews').
2. Zero-Quota RSS Extraction for recent uploads.
3. High-Conversion Cold Value-Audit generator for short-form video & thumbnail retainers.
"""

import os
import re
import urllib.parse
import asyncio
import xml.etree.ElementTree as ET
import httpx
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# Default Niche Search Queries for Automated Channel Discovery
DEFAULT_DISCOVERY_QUERIES = [
    "finance podcast india",
    "saas founder interview",
    "startup founder story india",
    "ai tools review creator"
]

# Static fallback channels if search is quiet
FALLBACK_CHANNELS = [
    {"name": "Ali Abdaal", "channel_id": "UCoOae5nYA7VqaXzerajD0lg"}
]

async def discover_creator_channels_by_keyword(client_http: httpx.AsyncClient, query: str) -> list[dict]:
    """Discovers active creator channels from YouTube public search RSS without API quotas."""
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.youtube.com/results?search_query={encoded_query}&sp=CAI%253D"  # Upload date sorted
    
    discovered = []
    try:
        res = await client_http.get(search_url, headers=HEADERS, timeout=10.0)
        if res.status_code == 200:
            # Extract channel IDs and names via regex pattern from search HTML
            channel_matches = re.findall(r'"channelId":"(UC[a-zA-Z0-9_-]{22})"', res.text)
            unique_channels = list(set(channel_matches))[:3]
            for ch_id in unique_channels:
                discovered.append({
                    "name": f"Creator ({ch_id[:8]})",
                    "channel_id": ch_id,
                    "niche": query
                })
    except Exception as e:
        print(f"[!] Discovery error for '{query}': {e}")
        
    return discovered

async def fetch_channel_recent_videos(client_http: httpx.AsyncClient, channel_id: str) -> list[dict]:
    """Pulls recent video uploads from public YouTube RSS XML feed."""
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        res = await client_http.get(url, headers=HEADERS, timeout=8.0)
        if res.status_code != 200:
            return []
        root = ET.fromstring(res.content)
        author_node = root.find(".//{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name")
        channel_title = author_node.text.strip() if author_node is not None and author_node.text else "Creator"
        
        entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")
        videos = []
        for entry in entries[:4]:
            title_node = entry.find("{http://www.w3.org/2005/Atom}title")
            link_node = entry.find("{http://www.w3.org/2005/Atom}link")
            title = title_node.text.strip() if (title_node is not None and title_node.text) else "Untitled"
            link = link_node.attrib.get("href", "") if link_node is not None else ""
            videos.append({"title": title, "link": link, "channel_name": channel_title})
        return videos
    except Exception:
        return []

async def generate_cold_creator_audit(creator_name: str, recent_videos: list[dict]) -> str:
    """Generates a high-conversion value audit pitch."""
    video_titles = "\n".join([f"- {v['title']}" for v in recent_videos])
    first_title = recent_videos[0]['title'] if recent_videos else "your recent upload"

    if not GEMINI_API_KEY:
        return (
            f"Hey {creator_name}! Really enjoyed '{first_title}'. "
            f"I noticed a simple pacing and thumbnail contrast tweak that usually boosts short-form retention by 15-20%. "
            f"I drafted a quick 1-concept high-CTR thumbnail redesign—would you like me to send it over?"
        )

    prompt = f"""
    You are an elite YouTube retention strategist and video editor writing a cold DM/email to creator: {creator_name}.
    
    THEIR RECENT VIDEOS:
    {video_titles}
    
    STRICT RULES:
    1. NEVER sound like generic agency spam ("I can edit your videos").
    2. Start with an authentic 1-sentence compliment referencing their actual video title: "{first_title}".
    3. Provide a concrete, constructive 1-point micro-critique regarding short-form hooks, kinetic captions, or thumbnail contrast.
    4. Offer a low-friction value sample: "I drafted a 15-second test cut / high-CTR thumbnail concept—would you like me to send it over?"
    5. Maximum length: 60-80 words in a natural, casual creator-to-creator tone.
    """
    
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception:
        return f"Hey {creator_name}! Loved '{first_title}'. Would you like me to send over a 15-second retention test cut for your next video?"

async def run_dynamic_creator_discovery(custom_query: str = None):
    print("=" * 60)
    print("[*] DYNAMIC YOUTUBE CREATOR RADAR & OUTBOUND AUDITOR (v2.0)")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    queries = [custom_query] if custom_query else DEFAULT_DISCOVERY_QUERIES
    
    async with httpx.AsyncClient() as client_http:
        all_channels = []
        for q in queries:
            print(f"[*] Discovering creator channels for: '{q}'...")
            channels = await discover_creator_channels_by_keyword(client_http, q)
            all_channels.extend(channels)
            
        if not all_channels:
            print("[*] Using verified fallback channels...")
            all_channels = FALLBACK_CHANNELS
            
        print(f"[+] Found {len(all_channels)} creator channels to audit.\n")
        
        for ch in all_channels:
            videos = await fetch_channel_recent_videos(client_http, ch["channel_id"])
            if not videos:
                continue
                
            real_name = videos[0].get("channel_name", ch["name"])
            audit_pitch = await generate_cold_creator_audit(real_name, videos)
            
            print("\n" + "#" * 60)
            print(f"[+] VALUE-AUDIT FOR: {real_name.upper()}")
            print(f"    Channel ID: {ch['channel_id']}")
            print(f"    Latest Video: {videos[0]['title']}")
            print("#" * 60)
            print(audit_pitch)
            print("=" * 60)

if __name__ == "__main__":
    import sys
    query_arg = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(run_dynamic_creator_discovery(query_arg))
