"""
External API client for Quote API integration
Handles HTTP requests, caching, and error management
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config.settings import get_settings

class QuoteAPIClient:
    """Client for Quote API with caching and error handling"""
    
    def __init__(self):
        self.settings = get_settings()
        self.cache: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
        # Fallback quotes for when API is unavailable
        self.fallback_quotes = [
            "The secret of getting ahead is getting started. - Mark Twain",
            "Success is the sum of small efforts repeated day in and day out. - Robert Collier",
            "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
            "The way to get started is to quit talking and begin doing. - Walt Disney",
            "Innovation distinguishes between a leader and a follower. - Steve Jobs",
            "Your limitation—it's only your imagination.",
            "Push yourself, because no one else is going to do it for you.",
            "Great things never come from comfort zones.",
            "Dream it. Wish it. Do it.",
            "Success doesn't just find you. You have to go out and get it."
        ]
    
    async def get_random_quote(self) -> Optional[str]:
        """
        Get a random motivational quote with caching and error handling
        Returns cached quote if available, otherwise fetches from API
        """
        cache_key = "random_quote"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            self.logger.debug("Returning cached quote")
            return self.cache[cache_key]["data"]
        
        try:
            # Fetch from API with timeout
            quote = await self._fetch_quote_from_api()
            
            if quote:
                # Cache the successful response
                self._cache_quote(cache_key, quote)
                self.logger.info("Successfully fetched and cached new quote from API")
                return quote
            else:
                # API returned empty response
                self.logger.warning("API returned empty quote, using fallback")
                return self._get_fallback_quote()
        
        except asyncio.TimeoutError:
            self.logger.error("Timeout while fetching quote from API")
            return self._get_fallback_quote()
        
        except aiohttp.ClientError as e:
            self.logger.error(f"HTTP client error while fetching quote: {e}")
            return self._get_fallback_quote()
        
        except Exception as e:
            self.logger.error(f"Unexpected error while fetching quote: {e}")
            return self._get_fallback_quote()
    
    async def _fetch_quote_from_api(self) -> Optional[str]:
        """Fetch quote from external API with timeout handling"""
        timeout = aiohttp.ClientTimeout(total=5.0)  # 5 second timeout
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(self.settings.QUOTE_API_URL) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract quote and author from API response
                        content = data.get("content", "").strip()
                        author = data.get("author", "").strip()
                        
                        if content:
                            if author:
                                return f"{content} - {author}"
                            else:
                                return content
                        else:
                            self.logger.warning("API returned empty content")
                            return None
                    else:
                        self.logger.error(f"API returned status code: {response.status}")
                        return None
            
            except asyncio.TimeoutError:
                self.logger.error("Request timed out")
                raise
            
            except aiohttp.ClientError as e:
                self.logger.error(f"Client error: {e}")
                raise
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_item = self.cache[cache_key]
        expiry_time = cached_item["expires_at"]
        
        return datetime.now() < expiry_time
    
    def _cache_quote(self, cache_key: str, quote: str) -> None:
        """Cache quote with expiration time"""
        expires_at = datetime.now() + timedelta(seconds=self.settings.QUOTE_CACHE_DURATION)
        
        self.cache[cache_key] = {
            "data": quote,
            "expires_at": expires_at,
            "cached_at": datetime.now()
        }
    
    def _get_fallback_quote(self) -> str:
        """Get a random fallback quote when API is unavailable"""
        import random
        return random.choice(self.fallback_quotes)
    
    async def get_quote_by_author(self, author: str) -> Optional[str]:
        """Get quote by specific author (bonus functionality)"""
        cache_key = f"quote_author_{author.lower()}"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        try:
            timeout = aiohttp.ClientTimeout(total=5.0)
            url = f"{self.settings.QUOTE_API_URL}?author={author}"
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data.get("content", "").strip()
                        quote_author = data.get("author", "").strip()
                        
                        if content:
                            formatted_quote = f"{content} - {quote_author}" if quote_author else content
                            self._cache_quote(cache_key, formatted_quote)
                            return formatted_quote
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error fetching quote by author {author}: {e}")
            return None
    
    def clear_cache(self) -> None:
        """Clear all cached quotes"""
        self.cache.clear()
        self.logger.info("Quote cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        total_cached = len(self.cache)
        valid_cached = sum(1 for key in self.cache if self._is_cache_valid(key))
        
        return {
            "total_cached_items": total_cached,
            "valid_cached_items": valid_cached,
            "expired_cached_items": total_cached - valid_cached,
            "cache_hit_ratio": valid_cached / max(total_cached, 1)
        }
