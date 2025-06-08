"""
Data management service for habit tracking
Handles persistent storage using JSON files
"""

import json
import logging
import os
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
from config.settings import get_settings

class DataManager:
    """Manages persistent data storage for the habit tracker bot"""
    
    def __init__(self):
        self.settings = get_settings()
        self.data_file = self.settings.DATA_FILE_PATH
        self.logger = logging.getLogger(__name__)
        self.data: Dict[str, Any] = {
            "users": {},
            "habits": {},
            "checkins": {},
            "banned_users": {},
            "bot_stats": {
                "total_commands": 0,
                "start_date": datetime.now().isoformat()
            }
        }
        
    async def initialize(self):
        """Initialize data manager and load existing data"""
        await self._ensure_data_directory()
        await self._load_data()
        self.logger.info("Data manager initialized successfully")
    
    async def _ensure_data_directory(self):
        """Ensure storage directory exists"""
        storage_dir = os.path.dirname(self.data_file)
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
            self.logger.info(f"Created storage directory: {storage_dir}")
    
    async def _load_data(self):
        """Load data from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # Merge with default structure to handle new fields
                    self.data.update(loaded_data)
                self.logger.info("Data loaded successfully from file")
            else:
                self.logger.info("No existing data file found, starting with empty data")
        except Exception as e:
            self.logger.error(f"Error loading data from file: {e}")
            # Continue with empty data if file is corrupted
    
    async def _save_data(self):
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False, default=str)
            self.logger.debug("Data saved successfully to file")
        except Exception as e:
            self.logger.error(f"Error saving data to file: {e}")
            raise
    
    # User management methods
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data by ID"""
        return self.data["users"].get(str(user_id))
    
    async def set_user_language(self, user_id: int, language: str):
        """Set user language preference"""
        user_key = str(user_id)
        if user_key not in self.data["users"]:
            self.data["users"][user_key] = {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat()
            }
        
        self.data["users"][user_key]["language"] = language
        self.data["users"][user_key]["last_active"] = datetime.now().isoformat()
        await self._save_data()
    
    async def update_user_activity(self, user_id: int):
        """Update user's last active timestamp"""
        user_key = str(user_id)
        if user_key in self.data["users"]:
            self.data["users"][user_key]["last_active"] = datetime.now().isoformat()
            await self._save_data()
    
    # Habit management methods
    async def add_habit(self, user_id: int, name: str, frequency: str) -> bool:
        """Add a new habit for user"""
        try:
            habit_id = str(uuid.uuid4())
            habit_data = {
                "id": habit_id,
                "user_id": user_id,
                "name": name,
                "frequency": frequency,
                "created_at": datetime.now().isoformat(),
                "active": True
            }
            
            self.data["habits"][habit_id] = habit_data
            await self._save_data()
            
            self.logger.info(f"Added habit '{name}' for user {user_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error adding habit: {e}")
            return False
    
    async def get_user_habits(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all active habits for a user"""
        user_habits = []
        for habit_id, habit_data in self.data["habits"].items():
            if (habit_data["user_id"] == user_id and 
                habit_data.get("active", True)):
                user_habits.append(habit_data)
        
        # Sort by creation date
        user_habits.sort(key=lambda x: x["created_at"])
        return user_habits
    
    async def get_habit(self, user_id: int, habit_id: str) -> Optional[Dict[str, Any]]:
        """Get specific habit by ID"""
        habit = self.data["habits"].get(habit_id)
        if habit and habit["user_id"] == user_id:
            return habit
        return None
    
    async def delete_habit(self, user_id: int, habit_id: str) -> bool:
        """Delete a habit (mark as inactive)"""
        try:
            habit = await self.get_habit(user_id, habit_id)
            if habit:
                self.data["habits"][habit_id]["active"] = False
                self.data["habits"][habit_id]["deleted_at"] = datetime.now().isoformat()
                await self._save_data()
                
                self.logger.info(f"Deleted habit {habit_id} for user {user_id}")
                return True
            return False
        
        except Exception as e:
            self.logger.error(f"Error deleting habit: {e}")
            return False
    
    # Check-in management methods  
    async def record_checkin(self, user_id: int, habit_id: str) -> bool:
        """Record a habit check-in for today"""
        try:
            today = date.today().isoformat()
            checkin_id = f"{habit_id}_{today}"
            
            # Check if already checked in today
            if checkin_id in self.data["checkins"]:
                return False
            
            checkin_data = {
                "id": checkin_id,
                "user_id": user_id,
                "habit_id": habit_id,
                "date": today,
                "timestamp": datetime.now().isoformat()
            }
            
            self.data["checkins"][checkin_id] = checkin_data
            await self._save_data()
            
            self.logger.info(f"Recorded check-in for habit {habit_id} by user {user_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error recording check-in: {e}")
            return False
    
    async def is_checked_in_today(self, user_id: int, habit_id: str) -> bool:
        """Check if user has checked in for this habit today"""
        today = date.today().isoformat()
        checkin_id = f"{habit_id}_{today}"
        
        checkin = self.data["checkins"].get(checkin_id)
        return checkin is not None and checkin["user_id"] == user_id
    
    async def get_current_streak(self, user_id: int, habit_id: str) -> int:
        """Calculate current streak for a habit"""
        try:
            current_date = date.today()
            streak = 0
            
            # Check backwards from today
            for i in range(365):  # Max 1 year lookback
                check_date = current_date - timedelta(days=i)
                checkin_id = f"{habit_id}_{check_date.isoformat()}"
                
                checkin = self.data["checkins"].get(checkin_id)
                if checkin and checkin["user_id"] == user_id:
                    streak += 1
                else:
                    break
            
            return streak
        
        except Exception as e:
            self.logger.error(f"Error calculating streak: {e}")
            return 0
    
    async def get_total_checkins(self, user_id: int, habit_id: str) -> int:
        """Get total number of check-ins for a habit"""
        count = 0
        for checkin_data in self.data["checkins"].values():
            if (checkin_data["user_id"] == user_id and 
                checkin_data["habit_id"] == habit_id):
                count += 1
        return count
    
    # Ban management methods
    async def ban_user(self, user_id: int, reason: str, banned_by: int) -> bool:
        """Ban a user"""
        try:
            user_key = str(user_id)
            self.data["banned_users"][user_key] = {
                "user_id": user_id,
                "reason": reason,
                "banned_by": banned_by,
                "banned_at": datetime.now().isoformat()
            }
            await self._save_data()
            
            self.logger.info(f"Banned user {user_id} by admin {banned_by}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error banning user: {e}")
            return False
    
    async def unban_user(self, user_id: int, unbanned_by: int) -> bool:
        """Unban a user"""
        try:
            user_key = str(user_id)
            if user_key in self.data["banned_users"]:
                del self.data["banned_users"][user_key]
                await self._save_data()
                
                self.logger.info(f"Unbanned user {user_id} by admin {unbanned_by}")
                return True
            return False
        
        except Exception as e:
            self.logger.error(f"Error unbanning user: {e}")
            return False
    
    async def is_user_banned(self, user_id: int) -> bool:
        """Check if user is banned"""
        return str(user_id) in self.data["banned_users"]
    
    async def get_ban_status(self, user_id: int) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Get ban status and details for a user"""
        user_key = str(user_id)
        ban_info = self.data["banned_users"].get(user_key)
        return ban_info is not None, ban_info
    
    # Statistics methods
    async def get_bot_statistics(self) -> Dict[str, Any]:
        """Get comprehensive bot statistics"""
        try:
            now = datetime.now()
            week_ago = now - timedelta(days=7)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # User statistics
            total_users = len(self.data["users"])
            active_users_7d = 0
            new_users_today = 0
            russian_users = 0
            english_users = 0
            
            for user_data in self.data["users"].values():
                # Active users in last 7 days
                if user_data.get("last_active"):
                    last_active = datetime.fromisoformat(user_data["last_active"])
                    if last_active >= week_ago:
                        active_users_7d += 1
                
                # New users today
                if user_data.get("created_at"):
                    created_at = datetime.fromisoformat(user_data["created_at"])
                    if created_at >= today_start:
                        new_users_today += 1
                
                # Language distribution
                lang = user_data.get("language", "en")
                if lang == "ru":
                    russian_users += 1
                else:
                    english_users += 1
            
            # Habit statistics
            active_habits = sum(1 for h in self.data["habits"].values() if h.get("active", True))
            total_habits = len(self.data["habits"])
            
            # Frequency analysis
            frequency_count = {}
            for habit in self.data["habits"].values():
                if habit.get("active", True):
                    freq = habit.get("frequency", "daily")
                    frequency_count[freq] = frequency_count.get(freq, 0) + 1
            
            most_popular_frequency = max(frequency_count, key=frequency_count.get) if frequency_count else "daily"
            
            # Check-in statistics
            total_checkins = len(self.data["checkins"])
            checkins_today = 0
            
            today_str = date.today().isoformat()
            for checkin in self.data["checkins"].values():
                if checkin.get("date") == today_str:
                    checkins_today += 1
            
            avg_habits_per_user = active_habits / max(total_users, 1)
            
            return {
                "total_users": total_users,
                "active_users_7d": active_users_7d,
                "new_users_today": new_users_today,
                "russian_users": russian_users,
                "english_users": english_users,
                "total_habits": total_habits,
                "active_habits": active_habits,
                "most_popular_frequency": most_popular_frequency,
                "total_checkins": total_checkins,
                "checkins_today": checkins_today,
                "avg_habits_per_user": avg_habits_per_user,
                "banned_users": len(self.data["banned_users"]),
                "total_commands": self.data["bot_stats"].get("total_commands", 0)
            }
        
        except Exception as e:
            self.logger.error(f"Error getting bot statistics: {e}")
            return {}
    
    async def increment_command_count(self):
        """Increment total command count"""
        self.data["bot_stats"]["total_commands"] = self.data["bot_stats"].get("total_commands", 0) + 1
        await self._save_data()
    
    async def get_all_active_users(self) -> List[Dict[str, Any]]:
        """Get all active users for broadcasting"""
        active_users = []
        week_ago = datetime.now() - timedelta(days=7)
        
        for user_data in self.data["users"].values():
            # Skip banned users
            if await self.is_user_banned(user_data["user_id"]):
                continue
            
            # Only include users active in last week
            if user_data.get("last_active"):
                last_active = datetime.fromisoformat(user_data["last_active"])
                if last_active >= week_ago:
                    active_users.append(user_data)
        
        return active_users

    async def increment_command_count(self):
        """Increment total command count"""
        self.data["bot_stats"]["total_commands"] = self.data["bot_stats"].get("total_commands", 0) + 1
        await self._save_data()

    async def get_bot_statistics(self) -> Dict[str, Any]:
        """Get comprehensive bot statistics"""
        try:
            now = datetime.now()
            week_ago = now - timedelta(days=7)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

            # User statistics
            total_users = len(self.data["users"])
            active_users_7d = 0
            new_users_today = 0
            russian_users = 0
            english_users = 0

            for user_data in self.data["users"].values():
                # Active users in last 7 days
                if user_data.get("last_active"):
                    last_active = datetime.fromisoformat(user_data["last_active"])
                    if last_active >= week_ago:
                        active_users_7d += 1

                # New users today
                if user_data.get("created_at"):
                    created_at = datetime.fromisoformat(user_data["created_at"])
                    if created_at >= today_start:
                        new_users_today += 1

                # Language distribution
                lang = user_data.get("language", "en")
                if lang == "ru":
                    russian_users += 1
                else:
                    english_users += 1

            # Habit statistics
            active_habits = sum(1 for h in self.data["habits"].values() if h.get("active", True))
            total_habits = len(self.data["habits"])

            # Frequency analysis
            frequency_count = {}
            for habit in self.data["habits"].values():
                if habit.get("active", True):
                    freq = habit.get("frequency", "daily")
                    frequency_count[freq] = frequency_count.get(freq, 0) + 1

            most_popular_frequency = max(frequency_count, key=frequency_count.get) if frequency_count else "daily"

            # Check-in statistics
            total_checkins = len(self.data["checkins"])
            checkins_today = 0

            today_str = date.today().isoformat()
            for checkin in self.data["checkins"].values():
                if checkin.get("date") == today_str:
                    checkins_today += 1

            avg_habits_per_user = active_habits / max(total_users, 1)

            return {
                "total_users": total_users,
                "active_users_7d": active_users_7d,
                "new_users_today": new_users_today,
                "russian_users": russian_users,
                "english_users": english_users,
                "total_habits": total_habits,
                "active_habits": active_habits,
                "most_popular_frequency": most_popular_frequency,
                "total_checkins": total_checkins,
                "checkins_today": checkins_today,
                "avg_habits_per_user": avg_habits_per_user,
                "banned_users": len(self.data["banned_users"]),
                "total_commands": self.data["bot_stats"].get("total_commands", 0)
            }

        except Exception as e:
            self.logger.error(f"Error getting bot statistics: {e}")
            return {}
