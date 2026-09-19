import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# Вставьте токен вашего бота
BOT_TOKEN = "xztsZ74"

# URL локального сервера модели
LOCAL_MODEL_URL = "http://127.0.0.1:1234/v1/chat/completions"

# Название модели (замените на правильное имя из вашего LM Studio)
MODEL_NAME = "model-identifier"

# Логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет, дружище! С чем тебе сегодня помочь?")

# Обработка вопросов от пользователя
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_question = update.message.text
    logging.info(f"Пользователь задал вопрос: {user_question}")

    # Параметры запроса
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Ты ассистент, который отвечает пользователю."},
            {"role": "user", "content": user_question}
        ],
        "temperature": 0.7
    }

    try:
        # Отправка запроса на локальный сервер модели
        response = requests.post(
            LOCAL_MODEL_URL,
            json=payload,
            timeout=200,
        )
        logging.info(f"HTTP статус ответа: {response.status_code}")
        logging.info(f"Текст ответа от модели: {response.text}")

        # Проверка на ошибки в ответе
        response.raise_for_status()
        response_data = response.json()

        # Извлечение ответа модели
        if "choices" in response_data and len(response_data["choices"]) > 0:
            model_reply = response_data["choices"][0]["message"]["content"]
        else:
            model_reply = "Ответ не получен. Проверьте настройки модели."

    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе к серверу: {e}")
        model_reply = f"Ошибка при запросе к серверу: {e}"
    except ValueError as e:
        logging.error(f"Ошибка обработки ответа от сервера: {e}")
        model_reply = f"Ошибка обработки ответа от сервера: {e}"

    # Отправка ответа пользователю
    await update.message.reply_text(model_reply)

# Основная функция для запуска бота
def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
