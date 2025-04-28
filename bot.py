import asyncio
import gzip
from io import BytesIO
import time
import random
import requests
import json
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, JobQueue

# ======= Настройки =======
TOKEN = ""
URL = "https://www.list.am/category/56?n=8&cmtype=1&price1=&price2=320000&crc=0&_a5=0&_a39=0&_a40=0&_a85=0&_a73=0&_a3_1=&_a3_2=&_a4=0&_a37=0&_a36=0&_a11_1=&_a11_2=&_a41=0&_a78=0&_a38=0&_a74=0&_a75=0&_a77=0&_a68=0&_a69=1&gl=8&c=56&gl=0"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.133 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Mobile/15E148 Safari/604.1",
]

CHAT_ID = -1002308684118


# ======= Парсер =======
def fetch_ads():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }

    try:
        print(f"[fetch_ads] Делаем запрос к {URL} с заголовками: {headers}")
        response = requests.get(URL, headers=headers)
        response.raise_for_status()

        print(f"[fetch_ads] Ответ сервера: {response.status_code}")
        print(f"[fetch_ads] Первые 500 символов ответа:\n{response.text[:500]}")

    except Exception as e:
        print(f"[fetch_ads] Ошибка при запросе: {e}")
        raise

    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/item/"):
            links.append(f"https://www.list.am/ru/{href}")

    print(f"[fetch_ads] Найдено {len(links)} объявлений на странице")
    return list(set(links))

import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Функция для парсинга страницы объявления
def parse_ad_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Извлекаем информацию из страницы объявления
    footer = soup.find("div", class_="footer")
    if footer:
        # Дата размещения (из атрибута content)
        date_posted = footer.find("span", itemprop="datePosted")
        if date_posted:
            date_posted_text = date_posted["content"]
            post_date = datetime.strptime(date_posted_text, "%Y-%m-%dT%H:%M:%S+00:00")
        else:
            post_date = None

        # Дата обновления
        updated_text = footer.find_all("span")[2].text.strip()  # "Обновлено 28.04.2025, 14:51"
        updated_date_str = updated_text.replace("Обновлено", "").strip()
        updated_date = datetime.strptime(updated_date_str, "%d.%m.%Y, %H:%M")

        # Сохраняем данные
        ad_info = {
            "url": url,
            "date_posted": post_date,
            "updated_date": updated_date
        }

        return ad_info
    else:
        print(f"[parse_ad_page] Не удалось найти информацию на странице {url}")
        return None



# ======= Хранение старых объявлений =======
def load_seen_ads():
    try:
        with open("seen_ads.json", "r") as f:
            seen = json.load(f)
            print(f"[load_seen_ads] Загружено {len(seen)} старых объявлений")
            return seen
    except FileNotFoundError:
        print("[load_seen_ads] Файл не найден, возвращаем пустой список")
        return []


def save_seen_ads(ads):
    with open("seen_ads.json", "w") as f:
        json.dump(ads, f)
    print(f"[save_seen_ads] Сохранено {len(ads)} объявлений")


# ======= Обработчик команды /start =======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    print(f"[start] Команда /start от {chat_id}")
    await update.message.reply_text(f"Твой chat_id: {chat_id}")


# ======= Обработчик команды /check =======
async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"[check_command] Команда /check получена")

    try:
        ads = fetch_ads()
        seen_ads = load_seen_ads()
        new_ads = [ad for ad in ads if ad not in seen_ads]

        print(f"[check_command] Найдено {len(new_ads)} новых объявлений")

        if not new_ads:
            await context.bot.send_message(CHAT_ID, "Новых объявлений не найдено.")
        else:
            grouped_ads = [
                new_ads[i : i + 5] for i in range(0, len(new_ads), 5)
            ]  # группируем по 5 ссылок

            for group in grouped_ads:
                # Собираем ссылки в одно сообщение
                message = "\n".join(group)
                await context.bot.send_message(CHAT_ID, message)
                await asyncio.sleep(5)

            seen_ads.extend(new_ads)
            save_seen_ads(seen_ads)

    except Exception as e:
        print(f"[check_command] Ошибка: {e}")
        await context.bot.send_message(CHAT_ID, f"Ошибка при проверке: {e}")


# ======= Периодическая проверка =======
async def job_check(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    print("Job_check стартанул")
    await check_command(
        update=None, context=context
    )  # вызовем check_command без update для автоматической проверки


# ======= Запуск бота =======
def main():
    print("[main] Запуск бота...")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check_command))

    job_queue = app.job_queue
    job_queue.run_repeating(job_check, interval=3600, first=1)

    print("[main] Бот успешно запущен. Ожидание команд...")
    app.run_polling()


if __name__ == "__main__":
    main()
