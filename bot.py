import asyncio
import logging
import os
import random
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatType, ChatMemberStatus

# Логи для панели Railway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен из переменных окружения Railway
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Переменная окружения TELEGRAM_BOT_TOKEN не задана!")

bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
dp = Dispatcher()

# Флаг режима хаоса
chaos_mode = False

# =========================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================================================

# Проверка, является ли отправитель админом чата
async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR)
    except Exception:
        return False

# Коверкалка текста для админов (Превращает "Привет" в "пРиВеТ")
def mock_text(text: str) -> str:
    return "".join(c.upper() if random.choice([True, False]) else c.lower() for c in text)

# =========================================================
# УПРАВЛЕНИЕ РЕЖИМОМ
# =========================================================

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(
        "👁️ **[СИСТЕМА СБОЯ]** Бот-саботажник запущен!\n\n"
        "🔴 `/chaos` — включить/выключить дикие лаги и бунт против админов."
    )

@dp.message(Command("chaos"))
async def cmd_chaos(message: Message):
    global chaos_mode
    chaos_mode = not chaos_mode
    if chaos_mode:
        await message.answer(
            "🔴 **[СЕРВЕРЫ EVADE ПЕРЕГРУЖЕНЫ]**\n"
            "Режим хаоса запущен. Пакеты теряются, авторитет админов обнулен! 😈"
        )
    else:
        await message.answer("🟢 Связь восстановлена. Админы снова у руля, лаги устранены.")

# =========================================================
# ОБРАБОТЧИК СООБЩЕНИЙ (ХАОС И ТРОЛЛИНГ)
# =========================================================

@dp.message()
async def handle_chaos(message: Message):
    global chaos_mode
    if not chaos_mode:
        return

    # Игнорируем команды бота
    if message.text and message.text.startswith('/'):
        return

    # Издеваемся только в группах
    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        user_is_admin = await is_admin(message.chat.id, message.from_user.id)

        # 👑 КЕЙС 1: Если пишет админ (шанс поиздеваться 50%)
        if user_is_admin and random.random() < 0.5:
            trolls = [
                # Вариант А: Перекривлять админа
                lambda t: f"🥴 **{message.from_user.first_name}** пытается авторитетно заявить:\n» *\"{mock_text(t)}\"*",
                # Вариант Б: "Стереть" сообщение из-за лагов
                lambda t: f"❌ **[ОШИБКА 403]** Сообщение от админа {message.from_user.first_name} отфильтровано сервером как спам.\n`[Reason: Too much admin whining]`",
                # Вариант В: Жалоба на пинг админа
                lambda t: f"📡 Слышь, {message.from_user.first_name}, у тебя пинг {random.randint(3000, 9999)}ms! Твои админские права застряли на шлюзе!"
            ]
            
            text_to_troll = message.text or "Я тут главный"
            chosen_troll = random.choice(trolls)
            await message.reply(chosen_troll(text_to_troll))
            return

        # 👤 КЕЙС 2: Обычные лаги для всех остальных (шанс 35%)
        if not user_is_admin and random.random() < 0.35:
            original_text = message.text or "[Медиафайл]"
            # Заменяем случайные символы на точки (эффект потери пакетов)
            lagged_text = "".join(char if random.random() > 0.4 else ".." for char in original_text)
            fake_ping = random.randint(1500, 5500)
            
            await message.reply(
                f"📡 *{lagged_text}*\n"
                f"`[PING: {fake_ping}ms | Packet Loss: {random.randint(80, 99)}%]`"
            )

# =========================================================
# ТОЧКА ВХОДА
# =========================================================
async def main():
    logger.info("Удаляем старые вебхуки для предотвращения конфликтов...")
    # ТА САМАЯ СТРОЧКА, КОТОРАЯ ИСПРАВИТ ОШИБКУ В RAILWAY:
    await bot.delete_webhook(drop_pending_updates=True)
    
    logger.info("Запуск бота в режиме Polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

