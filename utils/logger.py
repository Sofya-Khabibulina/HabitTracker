"""
Logging configuration and utilities
Provides structured logging for the habit tracker bot
"""

import logging
import os
from datetime import datetime
from typing import Optional
from config.settings import get_settings

def setup_logging() -> None:
    """Setup logging configuration for the application"""
    settings = get_settings()
    
    # Ensure logs directory exists
    log_dir = os.path.dirname(settings.LOG_FILE_PATH)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logging format
    log_format = (
        '%(asctime)s - %(name)s - %(levelname)s - '
        '[%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            # File handler
            logging.FileHandler(
                settings.LOG_FILE_PATH,
                encoding='utf-8'
            ),
            # Console handler
            logging.StreamHandler()
        ]
    )
    
    # Set specific log levels for different modules
    logging.getLogger('aiogram').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    # Create application-specific logger
    app_logger = logging.getLogger('habit_tracker')
    app_logger.setLevel(logging.INFO)
    
    app_logger.info("Logging system initialized")

def log_user_action(user_id: int, username: Optional[str], action: str, details: str = "") -> None:
    """
    Log user actions with structured format
    
    Args:
        user_id: Telegram user ID
        username: Telegram username (can be None)
        action: Action performed by user
        details: Additional details about the action
    """
    logger = logging.getLogger('habit_tracker.user_actions')
    
    username_str = username or "Unknown"
    timestamp = datetime.now().isoformat()
    
    log_message = f"USER_ACTION | {timestamp} | ID:{user_id} | @{username_str} | {action}"
    
    if details:
        log_message += f" | Details: {details}"
    
    logger.info(log_message)

def log_api_request(endpoint: str, status_code: int, response_time: float, error: str = "") -> None:
    """
    Log external API requests
    
    Args:
        endpoint: API endpoint called
        status_code: HTTP status code
        response_time: Request duration in seconds
        error: Error message if request failed
    """
    logger = logging.getLogger('habit_tracker.api_requests')
    
    timestamp = datetime.now().isoformat()
    log_message = f"API_REQUEST | {timestamp} | {endpoint} | Status:{status_code} | Time:{response_time:.3f}s"
    
    if error:
        log_message += f" | Error: {error}"
        logger.error(log_message)
    else:
        logger.info(log_message)

def log_system_event(event_type: str, message: str, level: str = "info") -> None:
    """
    Log system-level events
    
    Args:
        event_type: Type of system event
        message: Event description
        level: Log level (info, warning, error)
    """
    logger = logging.getLogger('habit_tracker.system')
    
    timestamp = datetime.now().isoformat()
    log_message = f"SYSTEM_EVENT | {timestamp} | {event_type} | {message}"
    
    if level.lower() == "error":
        logger.error(log_message)
    elif level.lower() == "warning":
        logger.warning(log_message)
    else:
        logger.info(log_message)

def log_performance_metric(metric_name: str, value: float, unit: str = "") -> None:
    """
    Log performance metrics
    
    Args:
        metric_name: Name of the metric
        value: Metric value
        unit: Unit of measurement
    """
    logger = logging.getLogger('habit_tracker.performance')
    
    timestamp = datetime.now().isoformat()
    unit_str = f" {unit}" if unit else ""
    log_message = f"PERFORMANCE | {timestamp} | {metric_name}: {value}{unit_str}"
    
    logger.info(log_message)

class StructuredLogger:
    """Structured logger for consistent log formatting"""
    
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)
    
    def log_habit_creation(self, user_id: int, habit_name: str, frequency: str) -> None:
        """Log habit creation event"""
        self.logger.info(
            f"HABIT_CREATED | UserID:{user_id} | Name:'{habit_name}' | Frequency:{frequency}"
        )
    
    def log_habit_checkin(self, user_id: int, habit_id: str, streak: int) -> None:
        """Log habit check-in event"""
        self.logger.info(
            f"HABIT_CHECKIN | UserID:{user_id} | HabitID:{habit_id} | Streak:{streak}"
        )
    
    def log_admin_action(self, admin_id: int, action: str, target_user: int = None) -> None:
        """Log administrative actions"""
        target_str = f" | TargetUser:{target_user}" if target_user else ""
        self.logger.info(
            f"ADMIN_ACTION | AdminID:{admin_id} | Action:{action}{target_str}"
        )
    
    def log_error_with_context(self, error: Exception, context: dict) -> None:
        """Log errors with additional context"""
        context_str = " | ".join([f"{k}:{v}" for k, v in context.items()])
        self.logger.error(
            f"ERROR | {type(error).__name__}: {str(error)} | Context: {context_str}"
        )

def get_structured_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance"""
    return StructuredLogger(f'habit_tracker.{name}')

class LoggerMixin:
    """Mixin class to add logging capabilities to other classes"""
    
    @property
    def logger(self):
        """Get logger for the class"""
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(f'habit_tracker.{self.__class__.__name__}')
        return self._logger
    
    def log_method_call(self, method_name: str, **kwargs):
        """Log method calls with parameters"""
        params = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        self.logger.debug(f"METHOD_CALL | {method_name} | {params}")
    
    def log_method_error(self, method_name: str, error: Exception):
        """Log method errors"""
        self.logger.error(f"METHOD_ERROR | {method_name} | {type(error).__name__}: {str(error)}")
