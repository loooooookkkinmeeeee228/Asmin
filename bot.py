import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatType, ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing!")

bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Состояние режима хаоса
chaos_mode = False

# Список целей для абсолютного стирания
TARGET_USERNAMES = []

# =========================================================
# ИНСТРУМЕНТЫ САБОТАЖА
# =========================================================

def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def glitch_text(text: str) -> str:
    glitch_chars = [
        "\u0300", "\u0301", "\u0302", "\u0303", "\u0304", "\u0305", "\u0306", "\u0307", "\u0308", "\u0309", 
        "\u030a", "\u030b", "\u030c", "\u030d", "\u030e", "\u030f", "\u0310", "\u0311", "\u0312", "\u0313", 
        "\u0314", "\u0315", "\u031a", "\u031b", "\u031c", "\u031d", "\u031e", "\u031f", "\u0320", "\u0321", 
        "\u0322", "\u0323", "\u0324", "\u0325", "\u0326", "\u0327", "\u0328", "\u032d", "\u032e", "\u032f", 
        "\u0330", "\u0331", "\u0332", "\u0333", "\u0334", "\u0335", "\u0336", "\u0337", "\u0338", "\u0339", 
        "\u033a", "\u033b", "\u033c", "\u033d", "\u033f", "\u0340", "\u0341", "\u0342", "\u0343", "\u0344", 
        "\u0345", "\u0346", "\u034a", "\u034b", "\u034c", "\u034d", "\u034e", "\u0350", "\u0351", "\u0352", 
        "\u0353", "\u0354", "\u0355", "\u0356", "\u0357", "\u0358", "\u035b", "\u035c", "\u035d", "\u035e", 
        "\u0360", "\u0361", "\u0362", "\u033e", "\u035a"
    ]
    res = []
    for char in text:
        res.append(char)
        if char.isalnum():
            # Накладываем максимальный слой искажения на каждый символ
            for _ in range(5):
                res.append(random_choice_local(glitch_chars))
    return "".join(res)

# Локальный быстрый выбор без импорта всего модуля random для оптимизации скорости
def random_choice_local(lst):
    import time
    t = int(time.time_ns())
    return lst[t % len(lst)]

async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR)
    except Exception:
        return False

async def send_ghost_ping(chat_id: int, target_username: str):
    try:
        msg = await bot.send_message(chat_id=chat_id, text=f"@{target_username}")
        await msg.delete()
    except Exception:
        pass

# =========================================================
# ОБРАБОТКА КОМАНД
# =========================================================

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply("В сети.")

@dp.message(Command("chaos"))
async def cmd_chaos(message: Message):
    global chaos_mode
    if message.chat.type != ChatType.PRIVATE:
        if not await is_admin(message.chat.id, message.from_user.id):
            return

    chaos_mode = not chaos_mode
    if chaos_mode:
        await message.answer("Атака запущена.")
    else:
        await message.answer("Связь восстановлена.")

# =========================================================
# БЕЗУСЛОВНЫЙ САБОТАЖ (100% ШАНС)
# =========================================================

@dp.message()
async def main_saboteur(message: Message):
    global chaos_mode
    if not chaos_mode:
        return

    if message.text and message.text.startswith('/chaos'):
        return

    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        sender = message.from_user
        username = sender.username.lower() if sender.username else ""
        user_is_admin = await is_admin(message.chat.id, sender.id)

        is_target = any(t.lower() == username for t in TARGET_USERNAMES)

        # 1. Если пишет katterx — удаление без исключений
        if is_target:
            try:
                await message.delete()
                return
            except TelegramBadRequest:
                pass

        # 2. Если пишет другой админ — удаление без исключений
        elif user_is_admin:
            try:
                await message.delete()
                return
            except TelegramBadRequest:
                pass

        # 3. Если пишет обычный юзер — 100% замена текста на глитч
        else:
            if message.text:
                try:
                    original_text = message.text
                    await message.delete()
                    glitched = glitch_text(escape_html(original_text))
                    await message.answer(f"<b>{sender.first_name}</b>: {glitched}")
                except TelegramBadRequest:
                    pass

        # 4. Призрачный пинг по целям запускается при любой активности в чате
        if not is_target:
            for target in TARGET_USERNAMES:
                asyncio.create_task(send_ghost_ping(message.chat.id, target))

# =========================================================
# ЗАПУСК
# =========================================================
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



