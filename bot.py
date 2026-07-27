import os
import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import json
import random

# 加载环境变量
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 8443))

# 机器人身份信息
BOT_USERNAME = "sophylove777bot"  # 您的机器人用户名
BOT_NAME = "QH"  # 机器人显示名称

# 启用日志记录
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== 搜索功能 ==========
def search_resources(query):
    """
    搜索功能 - 这里替换为真实的API调用
    目前使用模拟数据
    """
    # 模拟搜索结果 - 请替换为真实搜索逻辑
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
        return f"🔍 未找到与 '{query}' 相关的结果\n\n💡 尝试使用不同的关键词或联系 @hulian1688 获取高级搜索服务！"
    
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
    """发送欢迎消息 - 中文版"""
    user = update.effective_user
    welcome_text = f"""
👋 *欢迎使用 {BOT_NAME} 搜索机器人，{user.first_name}！*

🔍 *全球号商·搜一搜 资源搜索*

━━━━━━━━━━━━━━━━━━━━━

✨ *我能帮你做什么：*
• 📡 发现频道和群组
• 🔎 搜索资讯与热门内容
• 💎 国内外App账号批发
• ⚡ 快速精准搜索

━━━━━━━━━━━━━━━━━━━━━

📝 *如何使用：*
• 输入 `/搜索 [关键词]` 查找资源
• 例如：`/搜索 加密货币`
• 直接输入 `@{BOT_USERNAME} [关键词]` 快速搜索

━━━━━━━━━━━━━━━━━━━━━

💎 *官方客服：* @hulian1688
📢 *资源频道：* 即将上线

*祝您搜索愉快！* 🚀
"""
    keyboard = [
        [InlineKeyboardButton("🔍 立即搜索", switch_inline_query_current_chat="")],
        [InlineKeyboardButton("📢 加入频道", url="https://t.me/your_channel_here")],
        [InlineKeyboardButton("💎 官方客服", url="https://t.me/hulian1688")],
        [InlineKeyboardButton("❓ 使用帮助", callback_data="help")]
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
            f"例如：`/搜索 游戏账号`\n\n"
            f"💡 或使用内联搜索：`@{BOT_USERNAME} [关键词]`",
            parse_mode="Markdown"
        )
        return
    
    # 发送搜索中消息
    searching_msg = await update.message.reply_text(f"🔎 *正在搜索 '{query}'...*", parse_mode="Markdown")
    
    try:
        results = search_resources(query)
        formatted = format_results(results, query)
        await searching_msg.edit_text(formatted, parse_mode="Markdown", disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"搜索错误: {e}")
        await searching_msg.edit_text(
            "❌ *搜索出错啦！*\n\n"
            "请稍后重试或联系客服。\n"
            f"💎 客服支持：@hulian1688",
            parse_mode="Markdown"
        )

async def inline_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理内联搜索 (在任何聊天中输入 @sophylove777bot)"""
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
                        [{"text": "💎 高级服务", "url": "https://t.me/hulian1688"}]
                    ]
                }
            }
        )
    
    await update.inline_query.answer(inline_results)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """发送帮助信息 - 中文版"""
    help_text = f"""
📖 *QH 机器人使用帮助*

━━━━━━━━━━━━━━━━━━━━━

*📌 基本命令：*
/start - 欢迎页面
/搜索 [关键词] - 搜索资源
/帮助 - 显示帮助信息
/关于 - 关于机器人
/高级 - 高级服务信息

━━━━━━━━━━━━━━━━━━━━━

*⚡ 使用技巧：*
• 使用具体关键词获得更好结果
• 内联搜索：`@{BOT_USERNAME} [关键词]`
• 收藏本机器人以便快速访问

━━━━━━━━━━━━━━━━━━━━━

*💎 高级会员特权：*
• 无限次搜索
• 独家频道资源
• 优先客服支持
• 自定义搜索过滤器

━━━━━━━━━━━━━━━━━━━━━

*📞 联系我们：* @hulian1688
*🤖 机器人：* @{BOT_USERNAME}
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """发送关于信息 - 中文版"""
    about_text = f"""
🤖 *关于 QH 搜索机器人*

━━━━━━━━━━━━━━━━━━━━━

*强大的 Telegram 资源搜索引擎*
*版本：* 1.0.0
*用户名：* @{BOT_USERNAME}
*开发者：* @hulian1688

━━━━━━━━━━━━━━━━━━━━━

*✨ 功能特色：*
✅ 即时频道和群组搜索
✅ 热门内容发现
✅ 内联搜索支持
✅ 高级服务集成
✅ 24/7 全天候运行

━━━━━━━━━━━━━━━━━━━━━

*🔒 隐私保障：*
您的搜索记录安全私密。

*❤️ 为Telegram社区打造*
"""
    await update.message.reply_text(about_text, parse_mode="Markdown")

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """发送高级服务信息 - 中文版"""
    premium_text = f"""
💎 *QH 高级会员服务*

━━━━━━━━━━━━━━━━━━━━━

*🚀 会员特权：*

✅ *高级搜索*
- 无限次搜索
- 深度资源扫描
- 优先显示结果

✅ *独家访问*
- 私密频道
- 认证资源
- VIP专属内容

✅ *会员支持*
- 24小时客服
- 定制搜索请求
- 新功能优先体验

━━━━━━━━━━━━━━━━━━━━━

*💳 咨询价格：*
📞 @hulian1688

*🔗 资源频道：* 即将上线

━━━━━━━━━━━━━━━━━━━━━

*立即升级高级会员！* 🚀
"""
    keyboard = [
        [InlineKeyboardButton("💬 联系客服", url="https://t.me/hulian1688")],
        [InlineKeyboardButton("📢 关注更新", url="https://t.me/your_channel_here")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(premium_text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理按钮回调"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "help":
        await help_command(update, context)

# ========== 错误处理 ==========
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """记录错误日志"""
    logger.warning(f"更新 {update} 导致错误 {context.error}")

# ========== 主程序 ==========
def main():
    """启动机器人"""
    if not TOKEN:
        logger.error("未设置 BOT_TOKEN 环境变量！")
        return
    
    # 创建应用
    app = Application.builder().token(TOKEN).build()
    
    # 添加命令处理器 (中文命令)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("搜索", search))  # 中文命令
    app.add_handler(CommandHandler("帮助", help_command))  # 中文命令
    app.add_handler(CommandHandler("关于", about))  # 中文命令
    app.add_handler(CommandHandler("高级", premium))  # 中文命令
    
    # 保留英文命令作为别名（方便习惯英文的用户）
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("premium", premium))
    
    # 添加内联搜索处理器
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, inline_search))
    
    # 添加按钮回调处理器
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # 添加错误处理器
    app.add_error_handler(error_handler)
    
    logger.info(f"正在启动 {BOT_NAME} Bot (@{BOT_USERNAME})...")
    
    # 启动机器人 - 使用轮询模式 (Background Worker)
    app.run_polling(
        poll_interval=1.0,  # 每秒检查一次更新
        timeout=30,          # 长轮询超时时间
        drop_pending_updates=True  # 重启时跳过旧更新
    )

if __name__ == "__main__":
    main()
