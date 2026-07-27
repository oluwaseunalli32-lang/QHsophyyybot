import os
import sys
import logging
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
    InlineQueryHandler,
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Bot identity - Updated for your bot
BOT_USERNAME = "QHsophyyybot"  # Your bot's username
BOT_NAME = "QH"  # Display name
SUPPORT_USERNAME = "sophylove777"  # Changed to your username

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ========== DATA ==========
# Pre-defined search categories with sample results
# Replace these with real data or API integration later
SEARCH_CATEGORIES = {
    "热搜排行": [
        {"name": "🔥 今日热门话题", "link": "https://t.me/trending"},
        {"name": "📊 实时热搜榜", "link": "https://t.me/hotsearch"},
        {"name": "⭐ 本周热门推荐", "link": "https://t.me/weeklyhot"},
    ],
    "资讯": [
        {"name": "📰 新闻资讯频道", "link": "https://t.me/news"},
        {"name": "📡 实时资讯群组", "link": "https://t.me/liveinfo"},
        {"name": "📺 视频资讯推荐", "link": "https://t.me/videonews"},
    ],
    "军事": [
        {"name": "🎖️ 军事频道精选", "link": "https://t.me/military"},
        {"name": "🛡️ 国防资讯群组", "link": "https://t.me/defense"},
        {"name": "⚔️ 军事历史资源", "link": "https://t.me/militaryhistory"},
    ],
    "旅游": [
        {"name": "✈️ 旅游攻略频道", "link": "https://t.me/travel"},
        {"name": "🏝️ 旅游景点推荐", "link": "https://t.me/travelspots"},
        {"name": "🧳 旅行日记群组", "link": "https://t.me/traveldiary"},
    ],
    "福利": [
        {"name": "🎁 福利资源频道", "link": "https://t.me/freebies"},
        {"name": "💝 优惠活动群组", "link": "https://t.me/deals"},
        {"name": "🎊 限时福利推荐", "link": "https://t.me/limitedoffers"},
    ],
}

# ========== SEARCH FUNCTIONS ==========
def search_by_category(category):
    """Search by predefined category"""
    return SEARCH_CATEGORIES.get(category, [])

def search_by_keyword(keyword):
    """Search by keyword across all categories"""
    results = []
    keyword_lower = keyword.lower()
    for category, items in SEARCH_CATEGORIES.items():
        for item in items:
            if keyword_lower in item["name"].lower():
                results.append(item)
    return results[:10]  # Limit to 10 results

def format_search_results(results, query):
    """Format search results for display"""
    if not results:
        return f"🔍 没有找到与 '{query}' 相关的结果\n\n💡 试试其他关键词吧！"

    message = f"🔍 *搜索结果：{query}*\n"
    message += f"━━━━━━━━━━━━━━━━━\n\n"
    for i, res in enumerate(results, 1):
        message += f"{i}. [{res['name']}]({res['link']})\n"

    message += f"\n━━━━━━━━━━━━━━━━━\n"
    message += f"📌 *Powered by {BOT_NAME}* (@{BOT_USERNAME})\n"
    message += f"💎 *需要更多帮助？* @{SUPPORT_USERNAME}"
    return message

# ========== BOT COMMAND HANDLERS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start - Welcome message with inline keyboard"""
    user = update.effective_user
    first_name = user.first_name or "用户"

    # Welcome message replicating the reference bot's style
    welcome_text = f"""
👋 *Hi: {first_name}*

*欢迎使用{BOT_NAME}搜索机器人* 🔍

搜一搜轻松发现频道、群组、资讯与热门内容。

🔥 *热搜排行*

📌 *快捷分类：*
资讯 | 军事 | 旅游 | 福利

💡 *请输入关键词即可开始！*

━━━━━━━━━━━━━━━━━━━━━

👤 *您好，老板！我是人工客服 @{SUPPORT_USERNAME}，您需要什么业务？*
"""

    # Create inline keyboard buttons
    keyboard = [
        [
            InlineKeyboardButton("🔥 热搜排行", callback_data="category_热搜排行"),
            InlineKeyboardButton("📰 资讯", callback_data="category_资讯"),
        ],
        [
            InlineKeyboardButton("🎖️ 军事", callback_data="category_军事"),
            InlineKeyboardButton("✈️ 旅游", callback_data="category_旅游"),
        ],
        [
            InlineKeyboardButton("🎁 福利", callback_data="category_福利"),
            InlineKeyboardButton("📝 我的信息", callback_data="my_info"),
        ],
        [
            InlineKeyboardButton("💬 联系客服", url=f"https://t.me/{SUPPORT_USERNAME}"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        welcome_text, reply_markup=reply_markup, parse_mode="Markdown"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("category_"):
        # Handle category search
        category = data.replace("category_", "")
        results = search_by_category(category)

        if results:
            formatted = format_search_results(results, category)
            await query.edit_message_text(
                formatted, parse_mode="Markdown", disable_web_page_preview=True
            )
        else:
            await query.edit_message_text(f"❌ 没有找到 '{category}' 分类的内容")

    elif data == "my_info":
        # Show user information
        user = update.effective_user
        info_text = f"""
📝 *用户信息*

👤 *姓名：* {user.first_name or 'N/A'}
🆔 *用户名：* @{user.username or '未设置'}
📱 *ID：* {user.id}
🗓️ *首次使用：* {datetime.now().strftime('%Y-%m-%d %H:%M')}

━━━━━━━━━━━━━━━━━━━━━

*使用统计：*
📊 搜索次数：{context.user_data.get('search_count', 0)}
📌 已收藏：{context.user_data.get('favorites_count', 0)}

💎 *升级高级会员享受更多特权！*
联系客服：@{SUPPORT_USERNAME}
"""
        await query.edit_message_text(info_text, parse_mode="Markdown")

async def inline_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline search (user types keyword)"""
    query = update.inline_query.query.strip()

    if not query:
        # Show prompt when no keyword is entered
        prompt_text = "💡 请输入关键词开始搜索！\n\n例如：资讯、军事、旅游、福利"
        results = [
            {
                "type": "article",
                "id": "prompt",
                "title": "🔍 输入关键词搜索",
                "description": "输入关键词查找频道和群组",
                "input_message_content": {
                    "message_text": prompt_text,
                    "parse_mode": "Markdown",
                },
            }
        ]
        await update.inline_query.answer(results)
        return

    # Search by keyword
    results = search_by_keyword(query)

    if not results:
        # No results found
        no_results = [
            {
                "type": "article",
                "id": "no_results",
                "title": "❌ 没有找到结果",
                "description": f"没有找到与 '{query}' 相关的内容",
                "input_message_content": {
                    "message_text": f"🔍 没有找到与 '{query}' 相关的结果\n\n💡 试试其他关键词吧！",
                    "parse_mode": "Markdown",
                },
            }
        ]
        await update.inline_query.answer(no_results)
        return

    # Format inline results
    inline_results = []
    for i, res in enumerate(results[:10], 1):
        inline_results.append(
            {
                "type": "article",
                "id": str(i),
                "title": f"📌 {res['name']}",
                "description": f"搜索结果 - {query}",
                "input_message_content": {
                    "message_text": f"🔍 *搜索结果：*\n\n"
                                    f"📌 *{res['name']}*\n"
                                    f"🔗 {res['link']}\n\n"
                                    f"💎 *需要更多？* 联系 @{SUPPORT_USERNAME}",
                    "parse_mode": "Markdown",
                },
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "🔗 打开链接", "url": res['link']}],
                        [{"text": "🔄 更多搜索", "switch_inline_query": query}],
                        [{"text": "💬 联系客服", "url": f"https://t.me/{SUPPORT_USERNAME}"}],
                    ]
                },
            }
        )

    await update.inline_query.answer(inline_results)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages (not commands)"""
    user = update.effective_user
    text = update.message.text.strip()

    # Count searches
    if "search_count" not in context.user_data:
        context.user_data["search_count"] = 0
    context.user_data["search_count"] += 1

    # Search by keyword
    results = search_by_keyword(text)

    if results:
        formatted = format_search_results(results, text)
        await update.message.reply_text(
            formatted, parse_mode="Markdown", disable_web_page_preview=True
        )
    else:
        # No results found - suggest categories
        suggest_text = f"""
🔍 没有找到与 '{text}' 相关的结果

💡 *试试这些热门分类：*
• 资讯 - 最新新闻动态
• 军事 - 军事相关内容
• 旅游 - 旅游攻略推荐
• 福利 - 各种福利资源

📌 *或直接点击下方分类按钮快速查找！*

💎 *需要帮助？* @{SUPPORT_USERNAME}
"""
        keyboard = [
            [
                InlineKeyboardButton("🔥 热搜排行", callback_data="category_热搜排行"),
                InlineKeyboardButton("📰 资讯", callback_data="category_资讯"),
            ],
            [
                InlineKeyboardButton("🎖️ 军事", callback_data="category_军事"),
                InlineKeyboardButton("✈️ 旅游", callback_data="category_旅游"),
            ],
            [
                InlineKeyboardButton("🎁 福利", callback_data="category_福利"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            suggest_text, reply_markup=reply_markup, parse_mode="Markdown"
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = f"""
📖 *使用帮助*

━━━━━━━━━━━━━━━━━━━━━

*基本功能：*
• 输入关键词搜索频道和群组
• 点击下方分类按钮快速查找
• 使用内联搜索 @{BOT_USERNAME} [关键词]

━━━━━━━━━━━━━━━━━━━━━

*支持分类：*
📰 资讯 - 新闻资讯
🎖️ 军事 - 军事内容
✈️ 旅游 - 旅游攻略
🎁 福利 - 福利资源

━━━━━━━━━━━━━━━━━━━━━

*高级服务：*
💎 无限搜索
💎 独家资源
💎 优先支持

📞 *联系客服：* @{SUPPORT_USERNAME}
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    about_text = f"""
🤖 *关于{BOT_NAME}搜索机器人*

━━━━━━━━━━━━━━━━━━━━━

*版本：* 1.0.0
*开发者：* @{SUPPORT_USERNAME}
*平台：* Telegram

━━━━━━━━━━━━━━━━━━━━━

*功能特色：*
✅ 智能搜索频道和群组
✅ 热门分类快速查找
✅ 内联搜索支持
✅ 24/7 全天候运行

━━━━━━━━━━━━━━━━━━━━━

*❤️ 为Telegram社区打造*
"""
    await update.message.reply_text(about_text, parse_mode="Markdown")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")

# ========== MAIN ==========
def main():
    """Start the bot"""
    if not TOKEN:
        logger.error("❌ BOT_TOKEN not set!")
        return

    logger.info(f"🚀 Starting {BOT_NAME} Bot (@{BOT_USERNAME})...")

    try:
        # Create application
        app = Application.builder().token(TOKEN).build()

        # Add command handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("about", about))

        # Add inline query handler
        app.add_handler(InlineQueryHandler(inline_search))

        # Add message handler (for text input)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

        # Add button callback handler
        app.add_handler(CallbackQueryHandler(button_callback))

        # Add error handler
        app.add_error_handler(error_handler)

        logger.info("✅ Bot is ready!")
        logger.info("⏳ Listening for messages...")

        # Start polling
        app.run_polling(poll_interval=1.0, timeout=30, drop_pending_updates=True)

    except Exception as e:
        logger.error(f"❌ Failed to start: {e}")
        import traceback

        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
