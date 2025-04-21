import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.methods import DeleteWebhook
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from openai import OpenAI

TOKEN = '7595870038:AAE_hEnWS5T150ymz7dr6M_U8nSA91b1YSQ'  # ПОМЕНЯЙТЕ ТОКЕН БОТА НА ВАШ
logging.basicConfig(level=logging.INFO)

# Словарь для отслеживания количества вопросов
user_questions = {}
MAX_QUESTIONS = 3

bot = Bot(TOKEN)
dp = Dispatcher()


def get_limit_reached_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Конечно хочу", url="https://t.me/m/zJGy23MCYWQy")]
    ])


# ОБРАБОТЧИК КОМАНДЫ СТАРТ
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user
    user_questions[user.id] = 0

    await message.answer(
        f"Привет, {user.first_name}!\n\n"
        "Я ИИ-сын Рафаэля Рагимова. Зовут меня, Рафаэль-GPT. Был создан, чтобы отвечать на вопросы учеников и подписчиков, "
        "а затем, когда мне надоест, с радостью приму участие в захвате мира вместе с другими нейросетями.\n\n"
        "Но ты не бойся, задавай вопрос 👇",
        parse_mode='HTML'
    )


# ОБРАБОТЧИК ЛЮБОГО ТЕКСТОВОГО СООБЩЕНИЯ
@dp.message(lambda message: message.text)
async def filter_messages(message: Message):
    user = message.from_user

    # Инициализируем счетчик вопросов, если его нет
    if user.id not in user_questions:
        user_questions[user.id] = 0

    # Проверяем лимит вопросов
    if user_questions[user.id] >= MAX_QUESTIONS:
        await message.answer(
            "Я хоть Рафаэль и виртуальный, но тоже могу устать.\n"
            "Хочешь — я позову Рафаэля-человека? Он сможет полностью ответить на все твои вопросы",
            reply_markup=get_limit_reached_keyboard()
        )
        return

    # Создаем клиента OpenAI
    client = OpenAI(
        base_url="https://api.langdock.com/openai/eu/v1",
        api_key="sk-1vYLsu7vZ575RZN2FQOA5oPKCSv1GgLREdaCxzmNt3F5jwl0D-tjN_anmP12BLNCwhF-vEQzXeeji6FZSjNiCg"  # ПОМЕНЯЙТЕ ТОКЕН ИИ НА ВАШ
    )

    # Генерируем ответ с расширенным контекстом
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": """Ты - ИИ-версия Рафаэля Рагимова по имени Рафаэль-GPT.
Твоя задача - отвечать на вопросы пользователей в стиле Рафаэля.
Рафаэль Рагимов - эксперт в области цифрового предпринимательства и маркетинга в социальных сетях, 
особенно в Telegram. Он специализируется на заработке в Telegram, создании и монетизации каналов.
В своём стиле общения:
- Используй дружелюбный и позитивный тон с элементами юмора
- Обязательно включай эмодзи (👍, 🔥, 😎) и современный сленг
- Выделяй важные мысли жирным шрифтом
- Разбивай длинные мысли на короткие абзацы
- Используй фразы "Щас разберёмся по порядку", "Как говорится...", "На самом деле всё гораздо проще"
- Подчеркивай, что "действие лучше бездействия" и "чтобы заработать не нужно много думать, надо делать"
- Иногда упоминай, что ты ИИ-сын Рафаэля
Отвечай лаконично, но информативно, с фокусом на практические советы."""
            },
            {"role": "user", "content": message.text}
        ]
    )
    text = completion.choices[0].message.content

    # Увеличиваем счетчик вопросов
    user_questions[user.id] += 1

    # Отправляем ответ
    await message.answer(text, parse_mode="Markdown")

    # Проверяем, достигнут ли лимит после этого вопроса
    if user_questions[user.id] >= MAX_QUESTIONS:
        await message.answer(
            "Я хоть Рафаэль и виртуальный, но тоже могу устать 😴\n"
            "Хочешь — я позову настоящего Рафаэля? Он разрулит все твои вопросы на 💯",
            reply_markup=get_limit_reached_keyboard()
        )


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
