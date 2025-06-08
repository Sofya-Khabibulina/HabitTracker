"""
Reply keyboard builders for the bot
Provides quick access buttons and menu navigation
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from utils.localization import LocalizationManager

localization = LocalizationManager()

def get_main_menu_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Build main menu reply keyboard"""
    builder = ReplyKeyboardBuilder()
    
    # First row - primary actions
    add_habit_text = localization.get_text("menu_add_habit", lang)
    check_in_text = localization.get_text("menu_check_in", lang)
    
    builder.add(KeyboardButton(text=f"➕ {add_habit_text}"))
    builder.add(KeyboardButton(text=f"✅ {check_in_text}"))
    
    # Second row - information and management
    progress_text = localization.get_text("menu_progress", lang)
    habits_text = localization.get_text("menu_habits", lang)
    
    builder.add(KeyboardButton(text=f"📊 {progress_text}"))
    builder.add(KeyboardButton(text=f"🎯 {habits_text}"))
    
    # Third row - settings and help
    settings_text = localization.get_text("menu_settings", lang)
    help_text = localization.get_text("menu_help", lang)
    
    builder.add(KeyboardButton(text=f"⚙️ {settings_text}"))
    builder.add(KeyboardButton(text=f"❓ {help_text}"))
    
    # Adjust layout: 2 buttons per row
    builder.adjust(2, 2, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder=localization.get_text("menu_placeholder", lang)
    )

def get_habit_frequency_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Build frequency selection keyboard"""
    builder = ReplyKeyboardBuilder()
    
    # Frequency options
    daily_text = localization.get_text("frequency_daily", lang)
    weekly_text = localization.get_text("frequency_weekly", lang)
    three_times_text = localization.get_text("frequency_3_times", lang)
    
    builder.add(KeyboardButton(text=daily_text))
    builder.add(KeyboardButton(text=weekly_text))
    builder.add(KeyboardButton(text=three_times_text))
    
    # Cancel option
    cancel_text = localization.get_text("cancel_button", lang)
    builder.add(KeyboardButton(text=cancel_text))
    
    # Single column layout
    builder.adjust(1)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder=localization.get_text("frequency_placeholder", lang)
    )

def get_admin_menu_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Build admin menu keyboard"""
    builder = ReplyKeyboardBuilder()
    
    # Admin commands
    stats_text = localization.get_text("admin_stats", lang)
    broadcast_text = localization.get_text("admin_broadcast", lang)
    ban_text = localization.get_text("admin_ban_user", lang)
    
    builder.add(KeyboardButton(text=f"📊 {stats_text}"))
    builder.add(KeyboardButton(text=f"📢 {broadcast_text}"))
    builder.add(KeyboardButton(text=f"🚫 {ban_text}"))
    
    # Back to main menu
    main_menu_text = localization.get_text("back_to_main", lang)
    builder.add(KeyboardButton(text=f"🏠 {main_menu_text}"))
    
    # 2x2 layout
    builder.adjust(2, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder=localization.get_text("admin_placeholder", lang)
    )

def get_confirmation_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Build confirmation keyboard for destructive actions"""
    builder = ReplyKeyboardBuilder()
    
    confirm_text = localization.get_text("confirm_yes", lang)
    cancel_text = localization.get_text("confirm_no", lang)
    
    builder.add(KeyboardButton(text=f"✅ {confirm_text}"))
    builder.add(KeyboardButton(text=f"❌ {cancel_text}"))
    
    builder.adjust(2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder=localization.get_text("confirmation_placeholder", lang)
    )

def remove_keyboard() -> ReplyKeyboardMarkup:
    """Remove reply keyboard"""
    from aiogram.types import ReplyKeyboardRemove
    return ReplyKeyboardRemove()
