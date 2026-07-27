import os
import sys
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv

# Print Python version for debugging
print(f"🐍 Python version: {sys.version}")
print(f"📂 Python executable: {sys.executable}")

# 加载环境变量
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# 机器人身份信息
BOT_USERNAME = "sophylove777bot"
BOT_NAME = "QH"

# 启用日志记录
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== 搜索功能 ==========
def search_resources(query):
    """搜索功能 - 模拟数据，替换为真实API"""
    mock_results = [
        {"name": f"📡 {query} 频道精选", "link": f"https://t.me/example1_{query}"},
        {"name": f"👥 {query} 交流群组", "link": f"https://t.me/example2_{query}"},
        {"name": f"📰 {query} 最新资讯", "link": f"https://t.me/example3_{query}"},
        {"name": f"💎 {query} 优质资源", "link": f"https://t.me/example4_{query}"},
        {"name": f"🔍 {query} 深度搜索", "link": f"https://t.me/example5_{query}"},
    ]
    return mock_results[:5]

def format_results(results, query):
    """格式化搜索结果为中文消息"""
    if not results:
        return f"🔍 未找到与 '{query}' 相关的结果\n\n💡 联系 @hulian1688 获取高级搜索服务！"
    
    message = f"🔍 *搜索结果：{query}*\n"
    message += f"━━━━━━━━━━━━━━━━━\n\n"
    for i, res in enumerate(results, 1):
        message += f"{i}. [{res['name']}]({res['link']})\n"
    
    message += f"\n━━━━━━━━━━━━━━━━━\n"
    message += f"📌 *Powered by {BOT_NAME} Bot* (@{BOT_USERNAME})\n"
    message += f"💎 *需要更多结果？* 联系 @hulian1688"
    return message

# ========== 机器人命令处理 ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """发送欢迎消息"""
    user = update.effective_user
    welcome_text = f"""
👋 *欢迎使用 {BOT_NAME} 搜索机器人，{user.first_name}！*

🔍 *全球号商·搜一搜 资源搜索*

━━━━━━━━━━━━━━━━━━━━━

✨ *我能帮你做什么：*
• 📡 发现频道和群组
• 🔎 搜索资讯与热门内容
• 💎 国内外App账号批发

━━━━━━━━━━━━━━━━━━━━━

📝 *如何使用：*
• `/搜索 [关键词]` 查找资源
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
    """处理 /搜索 命令"""
    query = ' '.join(context.args)
    
    if not query:
        await update.message.reply_text(
            f"❌ *请提供搜索关键词！*\n\n"
            f"使用方法：`/搜索 [关键词]`\n"
            f"例如：`/搜索 游戏`\n\n"
            f"💡 或使用内联搜索：`@{BOT_USERNAME} [关键词]`",
            parse_mode="Markdown"
        )
        return
    
    searching_msg = await update.message.reply_text(f"🔎 *正在搜索 '{query}'...*", parse_mode="Markdown")
    
    try:
        results = search_resources(query)
        formatted = format_results(results, query)
        await searching_msg.edit_text(formatted, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"搜索错误: {e}")
        await searching_msg.edit_text(
            "❌ *搜索出错啦！*\n\n请稍后重试或联系客服。\n💎 客服：@hulian1688",
            parse_mode="Markdown"
        )

async def inline_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理内联搜索"""
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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """发送帮助信息"""
    help_text = f"""
📖 *QH 机器人使用帮助*

━━━━━━━━━━━━━━━━━━━━━

*📌 基本命令：*
/start - 欢迎页面
/搜索 [关键词] - 搜索资源
/帮助 - 显示帮助信息

━━━━━━━━━━━━━━━━━━━━━

*⚡ 使用技巧：*
• 使用具体关键词获得更好结果
• 内联搜索：`@{BOT_USERNAME} [关键词]`

━━━━━━━━━━━━━━━━━━━━━

*📞 联系我们：* @hulian1688
*🤖 机器人：* @{BOT_USERNAME}
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理按钮回调"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "help":
        await help_command(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """记录错误日志"""
    logger.error(f"更新 {update} 导致错误 {context.error}")

# ========== 主程序 ==========
def main():
    """启动机器人"""
    logger.info(f"🐍 Python version: {sys.version}")
    
    if not TOKEN:
        logger.error("❌ 未设置 BOT_TOKEN 环境变量！")
        return
    
    logger.info(f"🚀 正在启动 {BOT_NAME} Bot (@{BOT_USERNAME})...")
    logger.info(f"🔑 Token starts with: {TOKEN[:10]}...")
    
    try:
        # 创建应用
        app = Application.builder().token(TOKEN).build()
        logger.info("✅ Application built successfully")
        
        # 添加命令处理器
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("搜索", search))
        app.add_handler(CommandHandler("search", search))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("帮助", help_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, inline_search))
        app.add_error_handler(error_handler)
        
        logger.info("⏳ 机器人正在监听消息...")
        
        # 启动轮询
        app.run_polling(
            poll_interval=1.0,
            timeout=30,
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
