"""
Inline keyboard layouts for the bot
Provides interactive buttons for user interactions
"""

from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.localization import LocalizationManager

localization = LocalizationManager()

def get_language_keyboard() -> InlineKeyboardMarkup:
    """Create language selection keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")
        ]
    ])
    return keyboard

def get_habits_keyboard(habits: List[Dict[str, Any]], action: str, lang: str = "en") -> InlineKeyboardMarkup:
    """Create keyboard with user's habits for various actions"""
    keyboard_buttons = []

    for habit in habits:
        habit_id = habit["id"]
        habit_name = habit["name"]
        frequency = habit["frequency"]

        # Truncate long habit names for button display
        display_name = habit_name if len(habit_name) <= 25 else habit_name[:22] + "..."

        # Create button text with habit info
        button_text = f"{display_name} ({frequency})"
        callback_data = f"{action}_{habit_id}"

        keyboard_buttons.append([
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        ])

    # Add cancel button
    cancel_text = localization.get_text("cancel_button", lang)
    keyboard_buttons.append([
        InlineKeyboardButton(text=cancel_text, callback_data="cancel")
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return keyboard

def get_habit_actions_keyboard(habit_id: str, lang: str = "en") -> InlineKeyboardMarkup:
    """Create keyboard with available actions for a specific habit"""
    checkin_text = localization.get_text("checkin_button", lang)
    progress_text = localization.get_text("progress_button", lang)
    delete_text = localization.get_text("delete_button", lang)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"✅ {checkin_text}", callback_data=f"checkin_{habit_id}"),
        ],
        [
            InlineKeyboardButton(text=f"📊 {progress_text}", callback_data=f"progress_{habit_id}"),
        ],
        [
            InlineKeyboardButton(text=f"🗑 {delete_text}", callback_data=f"delete_{habit_id}"),
        ]
    ])
    return keyboard

def get_confirmation_keyboard(action: str, item_id: str, lang: str = "en") -> InlineKeyboardMarkup:
    """Create confirmation keyboard for destructive actions"""
    confirm_text = localization.get_text("confirm_button", lang)
    cancel_text = localization.get_text("cancel_button", lang)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"✅ {confirm_text}", callback_data=f"confirm_{action}_{item_id}"),
            InlineKeyboardButton(text=f"❌ {cancel_text}", callback_data="cancel")
        ]
    ])
    return keyboard

def get_frequency_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Create keyboard for selecting habit frequency"""
    daily_text = localization.get_text("frequency_daily", lang)
    weekly_text = localization.get_text("frequency_weekly", lang)
    three_times_text = localization.get_text("frequency_3_times", lang)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=daily_text, callback_data="freq_daily")],
        [InlineKeyboardButton(text=weekly_text, callback_data="freq_weekly")],
        [InlineKeyboardButton(text=three_times_text, callback_data="freq_3_times_week")],
        [InlineKeyboardButton(text=localization.get_text("cancel_button", lang), callback_data="cancel")]
    ])
    return keyboard

def get_admin_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Create admin panel keyboard"""
    stats_text = localization.get_text("admin_stats", lang)
    broadcast_text = localization.get_text("admin_broadcast", lang)
    ban_text = localization.get_text("admin_ban", lang)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📊 {stats_text}", callback_data="admin_stats")],
        [InlineKeyboardButton(text=f"📢 {broadcast_text}", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text=f"🚫 {ban_text}", callback_data="admin_ban")]
    ])
    return keyboard
