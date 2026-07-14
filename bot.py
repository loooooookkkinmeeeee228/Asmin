import asyncio
import logging
import os
import random
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatType

# Настройка логирования (чтобы видеть отчеты в панели Railway)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота берется из переменных окружения Railway
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Переменная окружения TELEGRAM_BOT_TOKEN не задана!")

# Инициализация бота с поддержкой форматирования Markdown
bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
dp = Dispatcher()

# Глобальный переключатель режима хаоса
chaos_mode = False

# =========================================================
# КОМАНДЫ МОДЕРАЦИИ
# =========================================================

# Команда /kick (выгнать игрока, но разрешить вернуться по ссылке)
@dp.message(Command("kick"))
async def cmd_kick(message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply("Эту команду можно использовать только в группе!")
        return

    if not message.reply_to_message:
        await message.reply("Ответь этой командой на сообщение того, кого хочешь кикнуть!")
        return

    target_user = message.reply_to_message.from_user
    try:
        # Трюк для кика: баним и сразу разбаниваем
        await message.chat.ban(user_id=target_user.id)
        await message.chat.unban(user_id=target_user.id)
        await message.answer(f"💨 Игрок *{target_user.first_name}* успешно выпнут из лобби! Дверь закрылась.")
    except Exception as e:
        await message.reply(f"❌ Не удалось кикнуть: `{e}`")

# Команда /ban (заблокировать навсегда)
@dp.message(Command("ban"))
async def cmd_ban(message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply("Эту команду можно использовать только в группе!")
        return

    if not message.reply_to_message:
        await message.reply("Ответь этой командой на сообщение того, кого хочешь забанить!")
        return

    target_user = message.reply_to_message.from_user
    try:
        await message.chat.ban(user_id=target_user.id)
        await message.answer(f"🔨 Игрок *{target_user.first_name}* отправлен в перманентный бан! 💀")
    except Exception as e:
        await message.reply(f"❌ Не удалось забанить: `{e}`")

# =========================================================
# УПРАВЛЕНИЕ РЕЖИМАМИ
# =========================================================

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(
        "👁️ **[СИСТЕМА]** Бот-вредитель запущен и готов к работе.\n\n"
        "🔴 `/chaos` — включить/выключить режим дикого пинга в группе.\n"
        "💨 `/kick` (в ответ на сообщение) — выгнать игрока.\n"
        "🔨 `/ban` (в ответ на сообщение) — забанить навсегда."
    )

@dp.message(Command("chaos"))
async def cmd_chaos(message: Message):
    global chaos_mode
    chaos_mode = not chaos_mode
    if chaos_mode:
        await message.answer(
            "🔴 **[ВНИМАНИЕ] РЕЖИМ ХАОСА АКТИВИРОВАН!** 🔴\n"
            "Сервера перегружены. Потери пакетов критические. Удачи поговорить! 😈"
        )
    else:
        await message.answer("🟢 Режим хаоса отключен. Пинг вернулся в норму, пакеты доходят стабильно.")

# =========================================================
# ПЕРЕХВАТЧИК СООБЩЕНИЙ (ГЕНЕРАТОР ЛАГОВ)
# =========================================================

@dp.message()
async def handle_ping_lag(message: Message):
    global chaos_mode
    
    # Пропускаем команды, чтобы не ломать их работу
    if message.text and message.text.startswith('/'):
        return

    # Портим жизнь только в групповых чатах и только при включенном хаосе
    if chaos_mode and message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        # Шанс 35%, что сообщение пользователя залагает
        if random.random() < 0.35:
            original_text = message.text or "[Медиафайл]"
            
            # Коверкаем текст (заменяем случайные символы на точки)
            lagged_chars = [char if random.random() > 0.4 else ".." for char in original_text]
            lagged_text = "".join(lagged_chars)
            
            # Генерируем фейковый пинг
            fake_ping = random.randint(990, 4999)
            
            await message.reply(
                f"📡 *{lagged_text}*\n"
                f"`[PING: {fake_ping}ms | Packet Loss: {random.randint(75, 99)}%]`"
            )

# =========================================================
# ТОЧКА ВХОДА И ЗАПУСК BOT POLLING
# =========================================================
async def main():
    logger.info("Старт бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
