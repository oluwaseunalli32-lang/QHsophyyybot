import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
import requests
import time

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Bot identity
BOT_USERNAME = "sophylove777bot"
BOT_NAME = "QH"

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== SEARCH FUNCTION ==========
def search_resources(query):
    """Search function - Replace with real search logic"""
    # Mock results - Replace with actual search
    mock_results = [
        {"name": f"📡 {query} 频道精选", "link": f"https://t.me/example1_{query}"},
        {"name": f"👥 {query} 交流群组", "link": f"https://t.me/example2_{query}"},
        {"name": f"📰 {query} 最新资讯", "link": f"https://t.me/example3_{query}"},
        {"name": f"💎 {query} 优质资源", "link": f"https://t.me/example4_{query}"},
    ]
    return mock_results[:5]

def format_results(results, query):
    """Format search results"""
    if not results:
        return f"🔍 未找到与 '{query}' 相关的结果\n\n💡 联系 @hulian1688 获取高级搜索服务！"
    
    message = f"🔍 *搜索结果：{query}*\n━━━━━━━━━━━━━━━━━\n\n"
    for i, res in enumerate(results, 1):
        message += f"{i}. [{res['name']}]({res['link']})\n"
    
    message += f"\n━━━━━━━━━━━━━━━━━\n"
    message += f"📌 *Powered by {BOT_NAME} Bot* (@{BOT_USERNAME})\n"
    message += f"💎 *客服：* @hulian1688"
    return message

# ========== BOT COMMAND HANDLERS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message"""
    user = update.effective_user
    welcome_text = f"""
👋 *欢迎使用 {BOT_NAME} 搜索机器人，{user.first_name}！*

🔍 *全球号商·搜一搜 资源搜索*

━━━━━━━━━━━━━━━━━━━━━

✨ *功能：*
• 📡 发现频道和群组
• 🔎 搜索资讯与热门内容
• 💎 国内外App账号批发

━━━━━━━━━━━━━━━━━━━━━

📝 *使用方法：*
• `/搜索 [关键词]` - 查找资源
• 例如：`/搜索 加密货币`

━━━━━━━━━━━━━━━━━━━━━

💎 *官方客服：* @hulian1688
"""
    keyboard = [
        [InlineKeyboardButton("🔍 立即搜索", switch_inline_query_current_chat="")],
        [InlineKeyboardButton("💎 官方客服", url="https://t.me/hulian1688")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search command"""
    query = ' '.join(context.args)
    
    if not query:
        await update.message.reply_text(
            f"❌ *请提供搜索关键词！*\n\n"
            f"使用方法：`/搜索 [关键词]`\n"
            f"例如：`/搜索 游戏`",
            parse_mode="Markdown"
        )
        return
    
    searching_msg = await update.message.reply_text(f"🔎 *正在搜索 '{query}'...*", parse_mode="Markdown")
    
    try:
        results = search_resources(query)
        formatted = format_results(results, query)
        await searching_msg.edit_text(formatted, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Search error: {e}")
        await searching_msg.edit_text(
            "❌ *搜索出错啦！*\n\n请稍后重试或联系客服。\n💎 客服：@hulian1688",
            parse_mode="Markdown"
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help message"""
    help_text = f"""
📖 *QH 机器人使用帮助*

📌 *基本命令：*
/start - 欢迎页面
/搜索 [关键词] - 搜索资源
/帮助 - 显示帮助信息

📞 *联系我们：* @hulian1688
🤖 *机器人：* @{BOT_USERNAME}
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def inline_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline search"""
    query = update.inline_query.query
    if not query:
        return
    
    results = search_resources(query)
    
    inline_results = []
    for i, res in enumerate(results[:10], 1):
        inline_results.append(
            {
                "type": "article",
                "id": str(i),
                "title": f"📌 {res['name']}",
                "description": f"由 {BOT_NAME} 机器人找到",
                "input_message_content": {
                    "message_text": f"🔍 *找到结果：*\n\n"
                                    f"📌 *{res['name']}*\n"
                                    f"🔗 {res['link']}\n\n"
                                    f"💎 *更多资源：* @hulian1688",
                    "parse_mode": "Markdown"
                },
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "🔗 打开链接", "url": res['link']}],
                        [{"text": "🔄 更多结果", "switch_inline_query": query}],
                    ]
                }
            }
        )
    
    await update.inline_query.answer(inline_results)

# ========== ERROR HANDLER ==========
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")

# ========== MAIN FUNCTION ==========
def main():
    """Start bot using polling (for background worker)"""
    if not TOKEN:
        logger.error("BOT_TOKEN not set!")
        return
    
    logger.info(f"Starting {BOT_NAME} Bot (@{BOT_USERNAME}) in polling mode...")
    
    # Create application
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("搜索", search))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("帮助", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, inline_search))
    app.add_error_handler(error_handler)
    
    # Start polling (this keeps running forever)
    logger.info("Bot is now running...")
    app.run_polling(
        poll_interval=1.0,  # Check for updates every second
        timeout=30,          # Timeout for long polling
        drop_pending_updates=True  # Skip old updates on restart
    )

if __name__ == "__main__":
    main()
