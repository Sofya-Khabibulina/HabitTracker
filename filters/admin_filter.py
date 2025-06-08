"""
Admin filter for restricting access to administrative commands
Checks if user ID is in the admin list from configuration
"""

from aiogram.filters import BaseFilter
from aiogram.types import Message
from config.settings import get_settings

class IsAdminFilter(BaseFilter):
    """Filter to check if user is an admin"""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def __call__(self, message: Message) -> bool:
        """Check if message sender is an admin"""
        if not message.from_user:
            return False
        
        user_id = message.from_user.id
        return user_id in self.settings.ADMIN_IDS

class IsBannedFilter(BaseFilter):
    """Filter to check if user is banned"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    async def __call__(self, message: Message) -> bool:
        """Check if message sender is banned"""
        if not message.from_user:
            return False
        
        user_id = message.from_user.id
        return await self.data_manager.is_user_banned(user_id)

class IsPrivateChatFilter(BaseFilter):
    """Filter to ensure command is used in private chat"""
    
    async def __call__(self, message: Message) -> bool:
        """Check if message is from private chat"""
        return message.chat.type == "private"

class CommandArgsFilter(BaseFilter):
    """Filter to check if command has required number of arguments"""
    
    def __init__(self, min_args: int = 1, max_args: int = None):
        self.min_args = min_args
        self.max_args = max_args
    
    async def __call__(self, message: Message) -> bool:
        """Check if command has required arguments"""
        if not message.text:
            return False
        
        args = message.text.split()[1:]  # Skip command itself
        arg_count = len(args)
        
        if arg_count < self.min_args:
            return False
        
        if self.max_args is not None and arg_count > self.max_args:
            return False
        
        return True

class TextLengthFilter(BaseFilter):
    """Filter to check text length constraints"""
    
    def __init__(self, min_length: int = 1, max_length: int = 1000):
        self.min_length = min_length
        self.max_length = max_length
    
    async def __call__(self, message: Message) -> bool:
        """Check if message text meets length requirements"""
        if not message.text:
            return False
        
        text_length = len(message.text.strip())
        return self.min_length <= text_length <= self.max_length
