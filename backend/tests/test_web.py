import pytest
from plugins.web_research import _web_scrape as web_scrape

@pytest.mark.asyncio
async def test_web_scrape_valid_url():
    """Test that the web scraper successfully fetches markdown from a known simple page."""
    # We use example.com as a fast, reliable target that doesn't change much.
    result = await web_scrape("https://example.com")
    
    assert "error" not in result
    assert "url" in result
    assert "markdown" in result
    
    md = result["markdown"].lower()
    assert "example domain" in md or "this domain is for use in illustrative examples" in md


@pytest.mark.asyncio
async def test_web_scrape_invalid_url():
    """Test that the web scraper handles invalid URLs gracefully."""
    result = await web_scrape("https://thisurldoesnotexist.xyz999")
    
    assert "error" in result
