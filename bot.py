"""
Habit Tracker Telegram Bot
Main entry point for the application
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config.settings import get_settings
from utils.logger import setup_logging
from middlewares.throttling import ThrottlingMiddleware
from routers import commands, admin
from services.data_manager import DataManager

async def main():
    """Main function to start the bot"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Load configuration
    settings = get_settings()
    
    # Initialize bot and dispatcher
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Setup middleware
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    
    # Include routers
    dp.include_router(commands.router)
    dp.include_router(admin.router)
    
    # Initialize data manager
    data_manager = DataManager()
    await data_manager.initialize()
    
    logger.info("Starting Habit Tracker Bot...")
    
    try:
        # Start polling
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
