"""
Throttling middleware to prevent spam and abuse
Implements rate limiting per user with configurable time windows
"""

import asyncio
import logging
from typing import Dict, Any, Awaitable, Callable
from datetime import datetime, timedelta

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from config.settings import get_settings

class ThrottlingMiddleware(BaseMiddleware):
    """Middleware for rate limiting user requests"""
    
    def __init__(self):
        self.settings = get_settings()
        self.rate_limit = self.settings.THROTTLE_RATE_LIMIT
        self.user_requests: Dict[int, datetime] = {}
        self.logger = logging.getLogger(__name__)
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process incoming updates with rate limiting"""
        
        # Extract user ID from different event types
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None
        
        # Skip throttling if we can't identify the user
        if user_id is None:
            return await handler(event, data)
        
        # Check rate limit
        if await self._is_rate_limited(user_id, event):
            self.logger.warning(f"Rate limit exceeded for user {user_id}")
            return  # Drop the update
        
        # Update last request time
        self.user_requests[user_id] = datetime.now()
        
        # Clean up old entries periodically
        await self._cleanup_old_entries()
        
        # Process the update
        return await handler(event, data)
    
    async def _is_rate_limited(self, user_id: int, event: TelegramObject) -> bool:
        """Check if user is rate limited"""
        if user_id not in self.user_requests:
            return False
        
        last_request = self.user_requests[user_id]
        time_diff = (datetime.now() - last_request).total_seconds()
        
        if time_diff < self.rate_limit:
            # Send throttling message for excessive requests
            await self._send_throttling_message(event, time_diff)
            return True
        
        return False
    
    async def _send_throttling_message(self, event: TelegramObject, time_diff: float):
        """Send rate limiting message to user"""
        try:
            wait_time = self.rate_limit - time_diff
            message_text = f"⏱ Please wait {wait_time:.1f} seconds before sending another message."
            
            if isinstance(event, Message):
                await event.answer(message_text)
            elif isinstance(event, CallbackQuery):
                await event.answer(message_text, show_alert=True)
        
        except Exception as e:
            self.logger.error(f"Error sending throttling message: {e}")
    
    async def _cleanup_old_entries(self):
        """Clean up old request timestamps to prevent memory leaks"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=1)
            users_to_remove = [
                user_id for user_id, timestamp in self.user_requests.items()
                if timestamp < cutoff_time
            ]
            
            for user_id in users_to_remove:
                del self.user_requests[user_id]
            
            if users_to_remove:
                self.logger.debug(f"Cleaned up {len(users_to_remove)} old throttling entries")
        
        except Exception as e:
            self.logger.error(f"Error during throttling cleanup: {e}")

class AntiFloodMiddleware(BaseMiddleware):
    """Advanced anti-flood middleware with progressive penalties"""
    
    def __init__(self, flood_threshold: int = 5, flood_window: int = 10):
        self.flood_threshold = flood_threshold  # Max messages per window
        self.flood_window = flood_window  # Time window in seconds
        self.user_message_count: Dict[int, list] = {}
        self.penalties: Dict[int, datetime] = {}
        self.logger = logging.getLogger(__name__)
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process updates with flood detection"""
        
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None
        
        if user_id is None:
            return await handler(event, data)
        
        # Check if user is currently penalized
        if await self._is_penalized(user_id):
            self.logger.warning(f"User {user_id} is penalized for flooding")
            return
        
        # Track message timing
        now = datetime.now()
        if user_id not in self.user_message_count:
            self.user_message_count[user_id] = []
        
        # Clean old messages outside the window
        self.user_message_count[user_id] = [
            msg_time for msg_time in self.user_message_count[user_id]
            if (now - msg_time).total_seconds() <= self.flood_window
        ]
        
        # Add current message
        self.user_message_count[user_id].append(now)
        
        # Check flood threshold
        if len(self.user_message_count[user_id]) > self.flood_threshold:
            await self._apply_penalty(user_id, event)
            return
        
        return await handler(event, data)
    
    async def _is_penalized(self, user_id: int) -> bool:
        """Check if user is currently penalized"""
        if user_id not in self.penalties:
            return False
        
        penalty_end = self.penalties[user_id]
        if datetime.now() >= penalty_end:
            del self.penalties[user_id]
            return False
        
        return True
    
    async def _apply_penalty(self, user_id: int, event: TelegramObject):
        """Apply flood penalty to user"""
        # Progressive penalty: 30 seconds, then 5 minutes, then 15 minutes
        penalty_duration = 30  # Start with 30 seconds
        
        if user_id in self.penalties:
            penalty_duration = min(penalty_duration * 3, 900)  # Max 15 minutes
        
        penalty_end = datetime.now() + timedelta(seconds=penalty_duration)
        self.penalties[user_id] = penalty_end
        
        self.logger.warning(f"Applied {penalty_duration}s flood penalty to user {user_id}")
        
        try:
            penalty_text = f"🚫 Flood detected! You are temporarily restricted for {penalty_duration} seconds."
            
            if isinstance(event, Message):
                await event.answer(penalty_text)
            elif isinstance(event, CallbackQuery):
                await event.answer(penalty_text, show_alert=True)
        
        except Exception as e:
            self.logger.error(f"Error sending penalty message: {e}")
