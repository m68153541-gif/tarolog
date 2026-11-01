import asyncio
import logging
import os
import random
from datetime import datetime, timedelta
from threading import Thread
from http.server import SimpleHTTPRequestHandler, HTTPServer

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telethon import TelegramClient
from telethon.sessions import StringSession

# ==========================================
# НАСТРОЙКИ
# ==========================================
BOT_TOKEN = "9217167507:AAEzoKBaNkroGJ5ISNOWIBGhwWPR5uTgP-4"
API_ID = 32969479
API_HASH = "817c78ce17662923f8167067b4551602"
ADMIN_ID = 8513244807

SESSION_STRING = os.environ.get("TG_SESSION_STRING", "")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Клиент Telethon (пока не используется для карт, но готов для отправки картинок)
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Хранилище состояний пользователей (для диалога)
user_states = {}

# ==========================================
# ВЕБ-СЕРВЕР ДЛЯ RENDER
# ==========================================
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    logging.info(f"Web server started on port {port}")
    server.serve_forever()

# ==========================================
# ТЕКСТЫ ПРЕДСКАЗАНИЙ (Много вариантов для рандома)
# ==========================================
LOVE_PREDICTIONS = [
    "💖 **Звёзды благоволят вам.** Скоро вы встретите человека, который перевернёт ваше представление о любви. Будьте открыты.",
    "❤️ **Вас ждёт страстный роман.** Но будьте осторожны: не все намерения чисты. Доверяйте интуиции.",
    "💔 **Временное охлаждение.** Не спешите с выводами. Иногда пауза нужна, чтобы понять истинные чувства.",
    "💍 **Судьбоносная встреча.** Человек, с которым вы встретитесь на этой неделе, может стать вашей судьбой.",
    "🌹 **Гармония в отношениях.** Если вы в паре — вас ждёт период нежности. Если одиноки — наслаждайтесь свободой."
]

CAREER_PREDICTIONS = [
    "💼 **Новый проект принесёт успех.** Не бойтесь брать на себя ответственность, звёзды на вашей стороне.",
    "💰 **Неожиданная прибыль.** Возможно, старый долг вернут или появится дополнительный источник дохода.",
    "⚖️ **Остерегайтесь конфликтов.** На работе возможны трения с коллегами. Сохраняйте спокойствие.",
    "🚀 **Карьерный рост.** Вас заметили. В ближайшие дни может поступить предложение о повышении.",
    "📉 **Временная задержка.** Не всё идёт по плану, но это не провал. Пересмотрите стратегию."
]

DAILY_PREDICTIONS = [
    "🌞 **День будет продуктивным.** Вы успеете всё, если не будете распыляться на мелочи.",
    "🌧 **Возможны мелкие неприятности.** Не расстраивайтесь, к вечеру всё наладится.",
    "🌪 **День перемен.** Будьте готовы к неожиданностям, они принесут вам пользу.",
    "🌙 **Время для отдыха.** Не перегружайте себя, позвольте себе расслабиться.",
    "🔥 **День энергии.** Вы сможете свернуть горы, если направите энергию в правильное русло."
]

# ==========================================
# ГЛАВНОЕ МЕНЮ
# ==========================================
def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔮 Получить предсказание", callback_data="get_prediction")
    builder.button(text="💖 Любовь", callback_data="love")
    builder.button(text="💼 Карьера", callback_data="career")
    builder.button(text="🌞 На день", callback_data="daily")
    builder.button(text="🃏 Вытянуть карту Таро", callback_data="tarot")
    builder.button(text="ℹ️ О боте", callback_data="about")
    builder.adjust(1, 2, 2, 1, 1)
    return builder.as_markup()

# ==========================================
# ОБРАБОТЧИКИ
# ==========================================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="🔮 Начать", callback_data="main_menu")
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я — **Мистический Таро-бот** 🔮. Я вижу скрытое и могу предсказать твоё будущее.\n\n"
        "Выбери, что тебя интересует:",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data == "main_menu")
async def process_main_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔮 **Главное меню**\n\n"
        "Выбери раздел, который тебя интересует:",
        reply_markup=get_main_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "get_prediction")
async def process_get_prediction(callback: CallbackQuery):
    prediction = random.choice(DAILY_PREDICTIONS + LOVE_PREDICTIONS + CAREER_PREDICTIONS)
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Ещё предсказание", callback_data="get_prediction")
    builder.button(text="⬅️ В меню", callback_data="main_menu")
    builder.adjust(1)
    await callback.message.edit_text(
        f"🔮 **Твоё предсказание:**\n\n{prediction}",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "love")
async def process_love(callback: CallbackQuery):
    prediction = random.choice(LOVE_PREDICTIONS)
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Ещё", callback_data="love")
    builder.button(text="⬅️ В меню", callback_data="main_menu")
    builder.adjust(1)
    await callback.message.edit_text(
        f"💖 **Предсказание в любви:**\n\n{prediction}",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "career")
async def process_career(callback: CallbackQuery):
    prediction = random.choice(CAREER_PREDICTIONS)
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Ещё", callback_data="career")
    builder.button(text="⬅️ В меню", callback_data="main_menu")
    builder.adjust(1)
    await callback.message.edit_text(
        f"💼 **Предсказание в карьере:**\n\n{prediction}",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "daily")
async def process_daily(callback: CallbackQuery):
    prediction = random.choice(DAILY_PREDICTIONS)
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Ещё", callback_data="daily")
    builder.button(text="⬅️ В меню", callback_data="main_menu")
    builder.adjust(1)
    await callback.message.edit_text(
        f"🌞 **Предсказание на день:**\n\n{prediction}",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "tarot")
async def process_tarot(callback: CallbackQuery):
    # Список карт Таро (названия и значения)
    tarot_cards = [
        ("Шут", "🌟 Новое начало, спонтанность, вера в лучшее."),
        ("Маг", "⚡ Сила воли, мастерство, проявление желаний."),
        ("Верховная Жрица", "🌙 Интуиция, тайные знания, подсознание."),
        ("Императрица", "🌸 Плодородие, творчество, изобилие."),
        ("Император", "🏛 Стабильность, власть, структура."),
        ("Иерофант", "📖 Традиции, обучение, духовный наставник."),
        ("Влюблённые", "💕 Выбор, союз, гармония."),
        ("Колесница", "🏇 Победа, воля, движение вперёд."),
        ("Сила", "🦁 Внутренняя сила, мужество, контроль эмоций."),
        ("Отшельник", "🕯 Уединение, поиск истины, мудрость."),
        ("Колесо Фортуны", "🎡 Судьба, перемены, цикличность."),
        ("Справедливость", "⚖️ Правда, закон, карма."),
        ("Повешенный", "🔄 Пауза, жертва, новый взгляд."),
        ("Смерть", "💀 Окончание, трансформация, rebirth."),
        ("Умеренность", "🧪 Баланс, гармония, терпение."),
        ("Дьявол", "😈 Искушение, зависимость, материализм."),
        ("Башня", "🌩 Разрушение, внезапные перемены, освобождение."),
        ("Звезда", "✨ Надежда, вдохновение, исцеление."),
        ("Луна", "🌕 Иллюзии, страхи, подсознание."),
        ("Солнце", "☀️ Радость, успех, жизненная сила."),
        ("Суд", "📯 Пробуждение, возрождение, расплата."),
        ("Мир", "🌍 Завершение, целостность, путешествия.")
    ]
    card_name, card_meaning = random.choice(tarot_cards)
    builder = InlineKeyboardBuilder()
    builder.button(text="🃏 Ещё карту", callback_data="tarot")
    builder.button(text="⬅️ В меню", callback_data="main_menu")
    builder.adjust(1)
    await callback.message.edit_text(
        f"🃏 **Твоя карта Таро:**\n\n"
        f"**{card_name}**\n"
        f"{card_meaning}",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "about")
async def process_about(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ В меню", callback_data="main_menu")
    await callback.message.edit_text(
        "ℹ️ **О боте**\n\n"
        "Этот бот — твой личный мистический помощник. Он не заменяет профессионального таролога, "
        "но может дать пищу для размышлений и подсказать направление.\n\n"
        "Все предсказания генерируются случайным образом на основе древних символов.\n\n"
        "✨ Используй его как игру и источник вдохновения!",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

# ==========================================
# ЗАПУСК
# ==========================================
async def main():
    t = Thread(target=run_dummy_server)
    t.daemon = True
    t.start()
    
    # Запускаем Telethon (он нужен, если вы захотите отправлять картинки карт)
    try:
        await client.start()
        logging.info("Telethon client started")
    except Exception as e:
        logging.error(f"Telethon error: {e}")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
