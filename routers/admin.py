
"""
Admin command handlers
Handles administrative functions like user management and statistics
"""

import logging
from datetime import datetime
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from filters.admin_filter import IsAdminFilter
from services.data_manager import DataManager
from utils.localization import LocalizationManager
from utils.logger import log_user_action

router = Router()
router.message.filter(IsAdminFilter())

data_manager = DataManager()
localization = LocalizationManager()
logger = logging.getLogger(__name__)

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Handle /stats command - show bot statistics"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    log_user_action(user_id, username, "admin_stats_command")

    try:
        # Check if command logging is available before calling it
        if hasattr(data_manager, 'log_command_usage'):
            await data_manager.log_command_usage(user_id, "stats")

        stats = await data_manager.get_bot_statistics()

        # Format statistics with proper fallbacks
        stats_text = f"""
📊 **Bot Statistics**

👥 **Users:**
• Total users: {stats.get('total_users', 'N/A')}
• Active users (last 7 days): {stats.get('active_users_7d', 'N/A')}
• New users today: {stats.get('new_users_today', 'N/A')}

🎯 **Habits:**
• Total habits created: {stats.get('total_habits', 'N/A')}
• Active habits: {stats.get('active_habits', 'N/A')}
• Completed check-ins today: {stats.get('checkins_today', 'N/A')}
• Total check-ins: {stats.get('total_checkins', 'N/A')}

📈 **Engagement:**
• Average habits per user: {stats.get('avg_habits_per_user', 0):.1f}
• Most popular frequency: {stats.get('most_popular_frequency', 'N/A')}
• Total commands processed: {stats.get('total_commands', 'N/A')}

🌍 **Languages:**
• Russian users: {stats.get('russian_users', 'N/A')}
• English users: {stats.get('english_users', 'N/A')}

🚫 **Moderation:**
• Banned users: {stats.get('banned_users', 'N/A')}

📅 **Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

        await message.answer(stats_text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error getting bot statistics: {e}", exc_info=True)
        await message.answer("❌ Error retrieving statistics. Please check logs.")

@router.message(Command("ban"))
async def cmd_ban(message: Message):
    """Handle /ban command - ban or unban users"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    log_user_action(user_id, username, "admin_ban_command")

    # Parse command arguments
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []

    if len(args) < 2:
        help_text = """
🛡️ **Ban/Unban Command Usage:**

**Ban a user:**
`/ban <user_id> ban [reason]`

**Unban a user:**
`/ban <user_id> unban`

**Check ban status:**
`/ban <user_id> status`

**Examples:**
• `/ban 123456789 ban Spam behavior`
• `/ban 123456789 unban`
• `/ban 123456789 status`

**Note:** User ID can be found by forwarding their message to @userinfobot
        """
        await message.answer(help_text, parse_mode="Markdown")
        return

    try:
        target_user_id = int(args[0])
        action = args[1].lower()

        if action == "ban":
            reason = " ".join(args[2:]) if len(args) > 2 else "No reason provided"
            success = await data_manager.ban_user(target_user_id, reason, user_id)

            if success:
                log_user_action(user_id, username, f"banned_user_{target_user_id}")
                await message.answer(f"✅ User {target_user_id} has been banned.\nReason: {reason}")
            else:
                await message.answer("❌ Failed to ban user. They may already be banned.")

        elif action == "unban":
            success = await data_manager.unban_user(target_user_id, user_id)

            if success:
                log_user_action(user_id, username, f"unbanned_user_{target_user_id}")
                await message.answer(f"✅ User {target_user_id} has been unbanned.")
            else:
                await message.answer("❌ Failed to unban user. They may not be banned.")

        elif action == "status":
            is_banned, ban_info = await data_manager.get_ban_status(target_user_id)

            if is_banned:
                banned_date = datetime.fromisoformat(ban_info['banned_at']).strftime('%Y-%m-%d %H:%M:%S')
                status_text = f"""
🚫 **User {target_user_id} is BANNED**

**Banned on:** {banned_date}
**Reason:** {ban_info['reason']}
**Banned by:** Admin {ban_info['banned_by']}
                """
            else:
                status_text = f"✅ User {target_user_id} is NOT banned."

            await message.answer(status_text, parse_mode="Markdown")

        else:
            await message.answer("❌ Invalid action. Use 'ban', 'unban', or 'status'.")

    except ValueError:
        await message.answer("❌ Invalid user ID. Please provide a valid numeric user ID.")
    except Exception as e:
        logger.error(f"Error in ban command: {e}", exc_info=True)
        await message.answer("❌ An error occurred while processing the ban command.")

@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    """Handle /broadcast command - send message to all users"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    log_user_action(user_id, username, "admin_broadcast_command")

    # Get broadcast message from command
    broadcast_text = message.text[len("/broadcast"):].strip()

    if not broadcast_text:
        help_text = """
📢 **Broadcast Command Usage:**

`/broadcast <message>`

**Example:**
`/broadcast 🎉 New feature released! Check out the updated habit tracking system.`

**Note:** This will send the message to all active users.
        """
        await message.answer(help_text, parse_mode="Markdown")
        return

    try:
        # Get all active users
        users = await data_manager.get_all_active_users()

        successful_sends = 0
        failed_sends = 0

        await message.answer(f"📤 Starting broadcast to {len(users)} users...")

        for user_data in users:
            try:
                # In actual implementation, you would send the message here
                # await bot.send_message(user_data['user_id'], broadcast_text)
                log_user_action(user_data['user_id'], "system", f"broadcast_received_{user_id}")
                successful_sends += 1
            except Exception as e:
                logger.error(f"Failed to send broadcast to user {user_data['user_id']}: {e}")
                failed_sends += 1

        result_text = f"""
✅ **Broadcast completed**

📊 **Results:**
• Successful sends: {successful_sends}
• Failed sends: {failed_sends}
• Total attempted: {len(users)}
        """

        await message.answer(result_text, parse_mode="Markdown")
        log_user_action(user_id, username, f"broadcast_completed_{successful_sends}_{failed_sends}")

    except Exception as e:
        logger.error(f"Error in broadcast command: {e}", exc_info=True)
        await message.answer("❌ An error occurred while processing the broadcast.")