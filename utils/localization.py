"""
Localization utilities for multi-language support
Handles text translations and language-specific formatting
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

class LocalizationManager:
    """Manages localization and translations for the bot"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.translations: Dict[str, Dict[str, str]] = {}
        self.supported_languages = ["en", "ru"]
        self.default_language = "en"
        self._load_translations()
    
    def _load_translations(self) -> None:
        """Load translation files from locales directory"""
        locales_dir = Path("locales")
        
        for lang in self.supported_languages:
            locale_file = locales_dir / f"{lang}.json"
            
            try:
                if locale_file.exists():
                    with open(locale_file, 'r', encoding='utf-8') as f:
                        self.translations[lang] = json.load(f)
                    self.logger.info(f"Loaded translations for language: {lang}")
                else:
                    self.logger.warning(f"Translation file not found: {locale_file}")
                    self.translations[lang] = {}
            
            except Exception as e:
                self.logger.error(f"Error loading translations for {lang}: {e}")
                self.translations[lang] = {}
    
    def get_text(self, key: str, language: str = "en", **kwargs) -> str:
        """
        Get localized text by key
        
        Args:
            key: Translation key
            language: Language code
            **kwargs: Format parameters for string formatting
        """
        # Fallback to default language if requested language not supported
        if language not in self.supported_languages:
            language = self.default_language
        
        # Get translation from requested language
        lang_translations = self.translations.get(language, {})
        text = lang_translations.get(key)
        
        # Fallback to default language if key not found
        if text is None and language != self.default_language:
            default_translations = self.translations.get(self.default_language, {})
            text = default_translations.get(key)
        
        # Final fallback to key itself if no translation found
        if text is None:
            self.logger.warning(f"Translation not found for key '{key}' in language '{language}'")
            text = key.replace("_", " ").title()
        
        # Format text with provided parameters
        try:
            if kwargs:
                text = text.format(**kwargs)
        except (KeyError, ValueError) as e:
            self.logger.error(f"Error formatting text for key '{key}': {e}")
        
        return text
    
    def get_language_name(self, language_code: str) -> str:
        """Get human-readable language name"""
        language_names = {
            "en": "English",
            "ru": "Русский"
        }
        return language_names.get(language_code, language_code)
    
    def is_supported_language(self, language_code: str) -> bool:
        """Check if language is supported"""
        return language_code in self.supported_languages
    
    def get_supported_languages(self) -> list:
        """Get list of supported language codes"""
        return self.supported_languages.copy()
    
    def format_frequency(self, frequency: str, language: str = "en") -> str:
        """Format habit frequency for display"""
        frequency_map = {
            "daily": {
                "en": "Daily",
                "ru": "Ежедневно"
            },
            "weekly": {
                "en": "Weekly", 
                "ru": "Еженедельно"
            },
            "3_times_week": {
                "en": "3 times a week",
                "ru": "3 раза в неделю"
            }
        }
        
        freq_translations = frequency_map.get(frequency, {})
        return freq_translations.get(language, frequency)
    
    def format_date(self, date_obj, language: str = "en") -> str:
        """Format date according to language preferences"""
        if language == "ru":
            # Russian date format: DD.MM.YYYY
            return date_obj.strftime("%d.%m.%Y")
        else:
            # English date format: MM/DD/YYYY
            return date_obj.strftime("%m/%d/%Y")
    
    def format_datetime(self, datetime_obj, language: str = "en") -> str:
        """Format datetime according to language preferences"""
        if language == "ru":
            # Russian format: DD.MM.YYYY HH:MM
            return datetime_obj.strftime("%d.%m.%Y %H:%M")
        else:
            # English format: MM/DD/YYYY HH:MM AM/PM
            return datetime_obj.strftime("%m/%d/%Y %I:%M %p")
    
    def pluralize(self, count: int, singular: str, plural: str, language: str = "en") -> str:
        """
        Handle pluralization based on language rules
        
        Args:
            count: Number to check
            singular: Singular form
            plural: Plural form  
            language: Language code
        """
        if language == "ru":
            # Russian pluralization is complex, simplified version
            if count % 10 == 1 and count % 100 != 11:
                return singular
            elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
                return plural
            else:
                return plural
        else:
            # English pluralization
            return singular if count == 1 else plural
    
    def format_streak_text(self, streak: int, language: str = "en") -> str:
        """Format streak text with proper pluralization"""
        if language == "ru":
            day_word = self.pluralize(streak, "день", "дней", "ru")
            return f"{streak} {day_word}"
        else:
            day_word = "day" if streak == 1 else "days"
            return f"{streak} {day_word}"
    
    def get_error_message(self, error_type: str, language: str = "en") -> str:
        """Get standardized error messages"""
        error_key = f"error_{error_type}"
        return self.get_text(error_key, language)
    
    def get_success_message(self, action: str, language: str = "en") -> str:
        """Get standardized success messages"""
        success_key = f"success_{action}"
        return self.get_text(success_key, language)
    
    def reload_translations(self) -> bool:
        """Reload translation files (useful for development)"""
        try:
            self._load_translations()
            self.logger.info("Translations reloaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error reloading translations: {e}")
            return False
