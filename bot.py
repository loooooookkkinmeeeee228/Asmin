import asyncio
import logging
import os
import random
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatType, ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest

# Настройка логирования для Railway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Переменная TELEGRAM_BOT_TOKEN отсутствует!")

# Используем HTML разметку — она надежнее Markdown и не падает от случайных символов
bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Флаг режима хаоса
chaos_mode = False

# =========================================================
# ВСПОМОГАТЕЛЬНЫЕ СКРИПТЫ
# =========================================================

# Экранирование HTML, чтобы бот не падал от символов "<" или ">" в чате
def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# Генератор жуткого глитч-текста (Zalgo)
def glitch_text(text: str) -> str:
    # Символы искажения Unicode
    glitch_chars = ["\u0300", "\u0301", "\u0302", "\u0303", "\u0304", "\u0305", "\u0309", "\u033f", "\u0324", "\u0330", "\u0332", "\u0333", "\u0334", "\u0335", "\u0336", "\u0337", "\u0338", "\u0320", "\u0325", "\u0327", "\u0328"]
    res = []
    for char in text:
        res.append(char)
        if char.isalnum() and random.random() < 0.4:
            for _ in range(random.randint(1, 3)):
                res.append(random.choice(glitch_chars))
    return "".join(res)

# Проверка на админа
async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR)
    except Exception:
        return False

# Скрытый Ghost Ping (вибрация есть — сообщения нет)
async def send_ghost_ping(chat_id: int, user_id: int, username: str):
    try:
        mention = f'<a href="tg://user?id={user_id}">@{username}</a>'
        msg = await bot.send_message(
            chat_id=chat_id,
            text=f"⚠️ {mention} <b>[SYSTEM EXCEPTION 0x011]</b> Thread conflict detected."
        )
        await msg.delete()  # Мгновенно стираем
    except Exception:
        pass

# =========================================================
# УПРАВЛЕНИЕ БОТОМ
# =========================================================

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(
        "👁️ <b>[СИСТЕМА]</b> Протокол Саботажа загружен.\n\n"
        "🔴 /chaos — активировать критические сетевые искажения."
    )

@dp.message(Command("chaos"))
async def cmd_chaos(message: Message):
    global chaos_mode
    # Переключать режим могут только админы группы или ты в ЛС
    if message.chat.type != ChatType.PRIVATE:
        user_is_admin = await is_admin(message.chat.id, message.from_user.id)
        if not user_is_admin:
            await message.reply("❌ <code>[ERROR] Access Denied: Unauthorized Terminal Connection.</code>")
            return

    chaos_mode = not chaos_mode
    if chaos_mode:
        await message.answer(
            "🔴 <b>[СЕТЕВАЯ АТАКА ЗАПУЩЕНА]</b>\n"
            "Серверы связи перегружены. Маршрутизация пакетов нарушена. "
            "Вся власть администраторов временно аннулирована. 💀"
        )
    else:
        await message.answer("🟢 <b>[СВЯЗЬ ВОССТАНОВЛЕНА]</b> Шлюзы очищены. Стабильность: 100%.")

# =========================================================
# ГЛАВНЫЙ ИСКАЗИТЕЛЬ (ПЕРЕХВАТЧИК СООБЩЕНИЙ)
# =========================================================

@dp.message()
async def main_saboteur(message: Message):
    global chaos_mode
    if not chaos_mode:
        return

    # Защита: команды управления ботом не трогаем
    if message.text and message.text.startswith('/chaos'):
        return

    # Работаем только в группах
    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        sender = message.from_user
        escaped_name = escape_html(sender.first_name)
        user_is_admin = await is_admin(message.chat.id, sender.id)

        # --- 🚨 СЛУЧАЙ 1: Саботаж админских команд (когда админ пишет любой /команду) ---
        if user_is_admin and message.text and message.text.startswith('/'):
            if random.random() < 0.65:  # 65% шанс сорвать команду админа
                try:
                    await message.delete()  # Стираем команду напрочь
                    await message.answer(
                        f"🚫 <b>[SECURITY FAILURE]</b> Command execution denied for "
                        f"user <code>@{sender.username or sender.id}</code>. Admin session certificate revoked."
                    )
                except TelegramBadRequest:
                    # Если у бота нет прав на удаление сообщений
                    await message.reply("⚠️ <code>[GATEWAY COLLISION] Core rejected admin command. Add bot as Admin.</code>")
                return

        # --- 💨 СЛУЧАЙ 2: Реальная потеря пакетов (Удаление обычных сообщений) ---
        drop_chance = 0.35 if user_is_admin else 0.20  # Для админов шанс выше!
        if random.random() < drop_chance:
            try:
                await message.delete()  # Удаляем сообщение из чата навсегда!
                
                if user_is_admin:
                    await message.answer(
                        f"🚨 <b>[GATEWAY CORRUPTION]</b> Message from Admin <b>{escaped_name}</b> "
                        f"was discarded by security buffer. <code>[Reason: Insecure payload]</code>"
                    )
                else:
                    await message.answer(
                        f"⚠️ <b>[PACKET LOSS]</b> Message from <b>{escaped_name}</b> "
                        f"dropped by gateway. <code>[CRC Error: 0x0A{random.randint(10,99)}F]</code>"
                    )
                return
            except TelegramBadRequest:
                # Если бот не админ группы, он физически не может удалить сообщения
                pass

        # --- 📡 СЛУЧАЙ 3: Искажение текста через Zalgo (Если сообщение выжило) ---
        if message.text and random.random() < 0.40:  # 40% шанс визуального глитча
            glitched = glitch_text(escape_html(message.text))
            fake_ping = random.randint(3500, 9999)
            
            await message.reply(
                f"📡 <code>[CON-LAG]</code> {glitched}\n"
                f"<code>[Latency: {fake_ping}ms | Loss: {random.randint(90,99)}%]</code>"
            )
            return

        # --- 👻 СЛУЧАЙ 4: Ghost Ping (Призрачный пинг админа) ---
        if not user_is_admin and random.random() < 0.10:  # 10% шанс при сообщении игрока затриггерить фантомный пинг
            # Ищем, кому отправить пинг (отправим автору сообщения, либо админу)
            await send_ghost_ping(message.chat.id, sender.id, sender.username or sender.first_name)

# =========================================================
# ЗАПУСК С ОЧИСТКОЙ
# =========================================================
async def main():
    logger.info("Сброс старых вебхуков...")
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Бот-саботажник успешно запущен в режиме Polling!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


