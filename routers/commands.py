"""
Main command handlers for user interactions
Handles basic bot commands and habit management
"""

import logging
from typing import Any, Dict
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from keyboards.inline import get_language_keyboard, get_habits_keyboard, get_habit_actions_keyboard
from keyboards.builders import get_main_menu_keyboard
from services.data_manager import DataManager
from services.api_client import QuoteAPIClient
from states.habit_states import HabitCreationStates
from utils.localization import LocalizationManager
from utils.logger import log_user_action

router = Router()
data_manager = DataManager()
quote_client = QuoteAPIClient()
localization = LocalizationManager()
logger = logging.getLogger(__name__)

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    
    log_user_action(user_id, username, "start_command")
    
    # Check if user exists and has language preference
    user_data = await data_manager.get_user(user_id)
    
    if not user_data or not user_data.get("language"):
        # New user or no language set - show language selection
        await message.answer(
            "🌍 Welcome to Habit Tracker Bot!\n"
            "Please select your language / Пожалуйста, выберите язык:",
            reply_markup=get_language_keyboard()
        )
    else:
        # Existing user with language preference
        lang = user_data["language"]
        welcome_text = localization.get_text("welcome_back", lang).format(
            name=message.from_user.first_name
        )
        await message.answer(
            welcome_text,
            reply_markup=get_main_menu_keyboard(lang)
        )

@router.callback_query(F.data.startswith("lang_"))
async def process_language_selection(callback: CallbackQuery):
    """Handle language selection"""
    user_id = callback.from_user.id
    username = callback.from_user.username or callback.from_user.full_name
    language = callback.data.split("_")[1]
    
    log_user_action(user_id, username, f"language_selected_{language}")
    
    # Save user language preference
    await data_manager.set_user_language(user_id, language)
    
    welcome_text = localization.get_text("welcome_new_user", language).format(
        name=callback.from_user.first_name
    )
    
    # Edit the original message without keyboard
    await callback.message.edit_text(welcome_text)
    
    # Send main menu keyboard as a separate message
    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text=localization.get_text("main_menu_prompt", language),
        reply_markup=get_main_menu_keyboard(language)
    )
    
    await callback.answer()

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    
    log_user_action(user_id, username, "help_command")
    
    user_data = await data_manager.get_user(user_id)
    lang = user_data.get("language", "en") if user_data else "en"
    
    help_text = localization.get_text("help_message", lang)
    await message.answer(help_text)

@router.message(Command("language"))
async def cmd_language(message: Message):
    """Handle /language command"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    
    log_user_action(user_id, username, "language_command")
    
    await message.answer(
        "🌍 Select language / Выберите язык:",
        reply_markup=get_language_keyboard()
    )

@router.message(Command("add_habit"))
async def cmd_add_habit(message: Message, state: FSMContext):
    """Handle /add_habit command - start FSM flow"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    
    log_user_action(user_id, username, "add_habit_command")
    
    user_data = await data_manager.get_user(user_id)
    lang = user_data.get("language", "en") if user_data else "en"
    
    # Start FSM for habit creation
    await state.set_state(HabitCreationStates.waiting_for_name)
    
    prompt_text = localization.get_text("add_habit_name_prompt", lang)
    await message.answer(prompt_text)

@router.message(HabitCreationStates.waiting_for_name)
async def process_habit_name(message: Message, state: FSMContext):
    """Process habit name input"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    habit_name = message.text.strip()
    
    if len(habit_name) < 2 or len(habit_name) > 50:
        user_data = await data_manager.get_user(user_id)
        lang = user_data.get("language", "en") if user_data else "en"
        error_text = localization.get_text("habit_name_length_error", lang)
        await message.answer(error_text)
        return
    
    # Store habit name and move to frequency selection
    await state.update_data(habit_name=habit_name)
    await state.set_state(HabitCreationStates.waiting_for_frequency)
    
    user_data = await data_manager.get_user(user_id)
    lang = user_data.get("language", "en") if user_data else "en"
    
    frequency_text = localization.get_text("add_habit_frequency_prompt", lang)
    await message.answer(frequency_text)

@router.message(HabitCreationStates.waiting_for_frequency)
async def process_habit_frequency(message: Message, state: FSMContext):
    """Process habit frequency input"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    frequency_text = message.text.strip().lower()
    
    # Map frequency input to standardized values
    frequency_map = {
        "daily": "daily", "каждый день": "daily", "ежедневно": "daily",
        "weekly": "weekly", "еженедельно": "weekly", "раз в неделю": "weekly",
        "3 times a week": "3_times_week", "3 раза в неделю": "3_times_week"
    }
    
    frequency = frequency_map.get(frequency_text)
    if not frequency:
        user_data = await data_manager.get_user(user_id)
        lang = user_data.get("language", "en") if user_data else "en"
        error_text = localization.get_text("invalid_frequency_error", lang)
        await message.answer(error_text)
        return
    
    # Get habit data and create habit
    state_data = await state.get_data()
    habit_name = state_data["habit_name"]
    
    success = await data_manager.add_habit(user_id, habit_name, frequency)
    
    user_data = await data_manager.get_user(user_id)
    lang = user_data.get("language", "en") if user_data else "en"
    
    if success:
        log_user_action(user_id, username, f"habit_created_{habit_name}_{frequency}")
        success_text = localization.get_text("habit_created_success", lang).format(
            habit_name=habit_name, frequency=frequency
        )
        await message.answer(success_text, reply_markup=get_main_menu_keyboard(lang))
    else:
        error_text = localization.get_text("habit_creation_error", lang)
        await message.answer(error_text)
    
    await state.clear()

@router.message(Command("check_in"))
async def cmd_check_in(message: Message):
    """Handle /check_in command"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    
    log_user_action(user_id, username, "check_in_command")
    
    user_data = await data_manager.get_user(user_id)
    lang = user_data.get("language", "en") if user_data else "en"
    
    habits = await data_manager.get_user_habits(user_id)
    
    if not habits:
        no_habits_text = localization.get_text("no_habits_message", lang)
        await message.answer(no_habits_text)
        return
    
    check_in_text = localization.get_text("select_habit_checkin", lang)
    await message.answer(
        check_in_text,
        reply_markup=get_habits_keyboard(habits, "checkin", lang)
    )

@router.callback_query(F.data.startswith("checkin_"))
async def process_habit_checkin(callback: CallbackQuery):
    """Process habit check-in"""
    user_id = callback.from_user.id
    username = callback.from_user.username or callback.from_user.full_name
    habit_id = callback.data.split("_")[1]
    
    user_data = await data_manager.get_user(user_id)
    lang = user_data.get("language", "en") if user_data else "en"
    
    # Check if already checked in today
    already_checked = await data_manager.is_checked_in_today(user_id, habit_id)
    
    if already_checked:
        error_text = localization.get_text("already_checked_in", lang)
        await callback.answer(error_text, show_alert=True)
        return
    
    # Record check-in
    success = await data_manager.record_checkin(user_id, habit_id)
    
    if success:
        log_user_action(user_id, username, f"habit_checkin_{habit_id}")
        
        # Get motivational quote
        quote = await quote_client.get_random_quote()
        
        habit = await data_manager.get_habit(user_id, habit_id)
        habit_name = habit["name"] if habit else "Unknown"
        
        success_text = localization.get_text("checkin_success", lang).format(
            habit_name=habit_name
        )
        
        if quote:
            success_text += f"\n\n💭 {quote}"
        
        await callback.message.edit_text(success_text)
    else:
        error_text = localization.get_text("checkin_error", lang)
        await callback.answer(error_text, show_alert=True)
    
    await callback.answer()

@router.message(Command("progress"))
async def cmd_progress(message: Message):
    """Handle /progress command"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    
    log_user_action(user_id, username, "progress_command")
    
    user_data = await data_manager.get_user(user_id)
    lang = user_data.get("language", "en") if user_data else "en"
    
    habits = await data_manager.get_user_habits(user_id)
    
    if not habits:
        no_habits_text = localization.get_text("no_habits_message", lang)
        await message.answer(no_habits_text)
        return
    
    progress_text = localization.get_text("progress_header", lang) + "\n\n"
    
    for habit in habits:
        habit_id = habit["id"]
        habit_name = habit["name"]
        frequency = habit["frequency"]
        current_streak = await data_manager.get_current_streak(user_id, habit_id)
        total_checkins = await data_manager.get_total_checkins(user_id, habit_id)
        
        habit_progress = localization.get_text("habit_progress_item", lang).format(
            name=habit_name,
            frequency=frequency,
            streak=current_streak,
            total=total_checkins
        )
        progress_text += habit_progress + "\n\n"
    
    await message.answer(progress_text)

@router.message(Command("delete_habit"))
async def cmd_delete_habit(message: Message):
    """Handle /delete_habit command"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    
    log_user_action(user_id, username, "delete_habit_command")
    
    user_data = await data_manager.get_user(user_id)
    lang = user_data.get("language", "en") if user_data else "en"
    
    habits = await data_manager.get_user_habits(user_id)
    
    if not habits:
        no_habits_text = localization.get_text("no_habits_message", lang)
        await message.answer(no_habits_text)
        return
    
    delete_text = localization.get_text("select_habit_delete", lang)
    await message.answer(
        delete_text,
        reply_markup=get_habits_keyboard(habits, "delete", lang)
    )

@router.callback_query(F.data.startswith("delete_"))
async def process_habit_deletion(callback: CallbackQuery):
    """Process habit deletion"""
    user_id = callback.from_user.id
    username = callback.from_user.username or callback.from_user.full_name
    habit_id = callback.data.split("_")[1]
    
    user_data = await data_manager.get_user(user_id)
    lang = user_data.get("language", "en") if user_data else "en"
    
    habit = await data_manager.get_habit(user_id, habit_id)
    if not habit:
        error_text = localization.get_text("habit_not_found", lang)
        await callback.answer(error_text, show_alert=True)
        return
    
    success = await data_manager.delete_habit(user_id, habit_id)
    
    if success:
        log_user_action(user_id, username, f"habit_deleted_{habit_id}")
        success_text = localization.get_text("habit_deleted_success", lang).format(
            habit_name=habit["name"]
        )
        await callback.message.edit_text(success_text)
    else:
        error_text = localization.get_text("habit_deletion_error", lang)
        await callback.answer(error_text, show_alert=True)
    
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def handle_cancel_button(callback: CallbackQuery):
    """Handle cancel button from inline keyboards"""
    user_id = callback.from_user.id
    username = callback.from_user.username or callback.from_user.full_name

    log_user_action(user_id, username, "cancel_button_pressed")

    user_data = await data_manager.get_user(user_id)
    lang = user_data.get("language", "en") if user_data else "en"

    cancel_text = localization.get_text("action_canceled", lang)
    await callback.message.edit_text(cancel_text)
    await callback.answer()


# Reply keyboard handlers for main menu buttons
@router.message(lambda message: message.text and (
    message.text.endswith("Добавить привычку") or 
    message.text.endswith("Add Habit")
))
async def handle_add_habit_button(message: Message, state: FSMContext):
    """Handle add habit button from reply keyboard"""
    await cmd_add_habit(message, state)

@router.message(lambda message: message.text and (
    message.text.endswith("Отметить выполнение") or 
    message.text.endswith("Check In")
))
async def handle_check_in_button(message: Message):
    """Handle check in button from reply keyboard"""
    await cmd_check_in(message)

@router.message(lambda message: message.text and (
    message.text.endswith("Прогресс") or 
    message.text.endswith("Progress")
))
async def handle_progress_button(message: Message):
    """Handle progress button from reply keyboard"""
    await cmd_progress(message)

@router.message(lambda message: message.text and (
    message.text.endswith("Мои привычки") or
    message.text.endswith("My Habits")
))
async def handle_habits_button(message: Message):
    """Handle habits management button from reply keyboard"""
    await cmd_delete_habit(message)

@router.message(lambda message: message.text and (
    message.text.endswith("Настройки") or
    message.text.endswith("Settings")
))
async def handle_settings_button(message: Message):
    """Handle settings button from reply keyboard"""
    await cmd_language(message)

@router.message(lambda message: message.text and (
    message.text.endswith("Помощь") or 
    message.text.endswith("Help")
))
async def handle_help_button(message: Message):
    """Handle help button from reply keyboard"""
    await cmd_help(message)
