"""
FSM states for habit creation and management
Defines state flows for interactive habit operations
"""

from aiogram.fsm.state import State, StatesGroup

class HabitCreationStates(StatesGroup):
    """States for habit creation flow"""
    waiting_for_name = State()
    waiting_for_frequency = State()
    confirming_creation = State()

class HabitEditingStates(StatesGroup):
    """States for habit editing flow"""
    selecting_habit = State()
    selecting_field = State()
    waiting_for_new_name = State()
    waiting_for_new_frequency = State()
    confirming_changes = State()

class HabitDeletionStates(StatesGroup):
    """States for habit deletion flow"""
    selecting_habit = State()
    confirming_deletion = State()

class ProgressViewStates(StatesGroup):
    """States for viewing detailed progress"""
    selecting_habit = State()
    selecting_time_period = State()
    viewing_details = State()

class AdminStates(StatesGroup):
    """States for admin operations"""
    selecting_action = State()
    waiting_for_user_id = State()
    waiting_for_ban_reason = State()
    waiting_for_broadcast_message = State()
    confirming_admin_action = State()

class LanguageStates(StatesGroup):
    """States for language selection and management"""
    selecting_language = State()
    confirming_language_change = State()

class SettingsStates(StatesGroup):
    """States for user settings management"""
    main_settings = State()
    notification_settings = State()
    privacy_settings = State()
    account_settings = State()

class OnboardingStates(StatesGroup):
    """States for new user onboarding"""
    welcome = State()
    language_selection = State()
    first_habit_setup = State()
    tutorial_completion = State()

class StatisticsStates(StatesGroup):
    """States for viewing statistics"""
    selecting_stats_type = State()
    selecting_time_range = State()
    viewing_detailed_stats = State()

class ExportStates(StatesGroup):
    """States for data export functionality"""
    selecting_export_format = State()
    selecting_data_range = State()
    confirming_export = State()
    generating_export = State()
