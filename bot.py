import asyncio
import random
import time
from datetime import datetime
import requests
import json
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

# ======= Настройки =======
TOKEN = os.getenv("BOT_TOKEN")
URL = "https://www.list.am/category/56?n=8&cmtype=1&price1=&price2=320000&crc=0&_a5=0&_a39=0&_a40=0&_a85=0&_a73=0&_a3_1=&_a3_2=&_a4=0&_a37=0&_a36=0&_a11_1=&_a11_2=&_a41=0&_a78=0&_a38=0&_a74=0&_a75=0&_a77=0&_a68=0&_a69=1&gl=8&c=56&gl=0"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.133 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:113.0) Gecko/20100101 Firefox/113.0",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.133 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.146 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",  # Internet Explorer 11
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.136 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_7_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",
]

ACCEPT_LANGUAGES = [
    "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "en-US,en;q=0.9,ru;q=0.8",
    "ru,en;q=0.9",
    "en;q=0.8",
]


def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": random.choice(ACCEPT_LANGUAGES),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
    }


CHAT_ID = -1002308684118

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "eu-US,en;q=0.9",
    "Referer": "https://www.list.am/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


# ======= Парсер =======
def fetch_ads():
    attempt = 0
    while True:
        try:
            dynamic_headers = get_random_headers()
            print(
                f"[fetch_ads] Попытка {attempt + 1}: Делаем запрос к {URL} \nUser-Agent: {dynamic_headers['User-Agent']}"
            )
            response = requests.get(URL, headers=dynamic_headers, timeout=10)
            response.raise_for_status()

            print(f"[fetch_ads] Ответ сервера: {response.status_code}")
            print(f"[fetch_ads] Первые 500 символов ответа:\n{response.text[:500]}")

            soup = BeautifulSoup(response.text, "html.parser")
            links = []

            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("/item/"):
                    links.append(f"https://www.list.am/ru{href}")

            print(f"[fetch_ads] Найдено {len(links)} объявлений на странице")
            return list(set(links))

        except Exception as e:
            attempt += 1
            print(
                f"[fetch_ads] Ошибка на попытке {attempt}: {e}. Ждём 10 секунд перед новой попыткой..."
            )
            time.sleep(10)


# Функция для парсинга страницы объявленияimport time
def parse_ad_page(url):
    attempts = 5  # Количество попыток
    for attempt in range(1, attempts + 1):
        try:
            dynamic_headers = get_random_headers()
            print(
                f"[parse_ad_page] Попытка {attempt} для {url} с User-Agent: {dynamic_headers['User-Agent']}"
            )
            response = requests.get(url, headers=dynamic_headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            footer = soup.find("div", class_="footer")
            if not footer:
                print(f"[parse_ad_page] Не найден футер на странице {url}")

            # Дата публикации
            date_posted = footer.find("span", itemprop="datePosted")
            if date_posted:
                date_posted_text = date_posted["content"]
                post_date = datetime.strptime(
                    date_posted_text, "%Y-%m-%dT%H:%M:%S+00:00"
                )
            else:
                post_date = None

            # Дата обновления
            updated_date = None
            updated_text = footer.find_all("span")
            if (
                isinstance(updated_text, list) and len(updated_text) > 2
            ):  # Проверка, что это список и есть 3 элемента
                updated_date_str = (
                    updated_text[2].text.strip().replace("Обновлено", "").strip()
                )
                try:
                    updated_date = datetime.strptime(
                        updated_date_str, "%d.%m.%Y, %H:%M"
                    )
                except ValueError:
                    updated_date = None  # Если формат даты неправильный

            # Парсим стоимость
            price_element = soup.find("span", class_="price x")
            if price_element:
                price = price_element.get_text(
                    strip=True
                )  # Берем именно текст между тегами
            else:
                price = "Не указана"

            # Возвращаем информацию
            ad_info = {
                "url": url,
                "date_posted": post_date,
                "updated_date": updated_date,
                "price": price,
            }

            return ad_info

        except requests.exceptions.RequestException as e:
            print(f"[parse_ad_page] Попытка {attempt} не удалась для {url}: {e}")
            if attempt < attempts:
                # Задержка между попытками
                time.sleep(10)
            else:
                print(f"[parse_ad_page] Ошибка при парсинге {url}: {e}")
                return None


# ======= Хранение старых объявлений =======
def load_seen_ads():
    try:
        with open("seen_ads.json", "r") as f:
            seen = json.load(f)
            print(f"[load_seen_ads] Загружено {len(seen)} старых объявлений")

            # Преобразуем строки обратно в datetime
            for ad_url, ad_data in seen.items():
                if ad_data.get("date_posted"):
                    ad_data["date_posted"] = datetime.fromisoformat(
                        ad_data["date_posted"]
                    )  # Преобразуем строку обратно в datetime
                if ad_data.get("updated_date"):
                    ad_data["updated_date"] = datetime.fromisoformat(
                        ad_data["updated_date"]
                    )  # Преобразуем строку обратно в datetime

            return seen
    except FileNotFoundError:
        print("[load_seen_ads] Файл не найден, возвращаем пустой список")
        return {}


def save_seen_ads(ads):
    # Преобразуем даты в строки для сохранения
    for ad_url, ad_data in ads.items():
        if ad_data.get("date_posted"):
            ad_data["date_posted"] = ad_data[
                "date_posted"
            ].isoformat()  # Преобразуем datetime в строку
        if ad_data.get("updated_date"):
            ad_data["updated_date"] = ad_data[
                "updated_date"
            ].isoformat()  # Преобразуем datetime в строку

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
        now = datetime.utcnow()

        new_ads = []
        updated_ads = []

        for ad_url in ads:
            ad_data = seen_ads.get(ad_url)
            if not ad_data:
                # Объявление совсем новое
                print(f"[check_command] Новое объявление {ad_url}")
                ad_info = parse_ad_page(ad_url)
                if ad_info is None:
                    print(
                        f"[check_command] Не удалось распарсить новое объявление {ad_url}"
                    )
                    continue

                new_ads.append(ad_url)
                seen_ads[ad_url] = {
                    "url": ad_url,
                    "first_seen": now.isoformat(),
                    "last_checked": now.isoformat(),
                    "date_posted": ad_info.get("date_posted", "Не указана"),
                    "updated_date": ad_info.get("updated_date", "Не указана"),
                    "price": ad_info.get("price", "Не указана"),
                }

            else:
                # Объявление уже есть в базе
                last_checked = datetime.fromisoformat(ad_data["last_checked"])
                if now - last_checked > timedelta(hours=3):
                    print(f"[check_command] Проверяем старое объявление {ad_url}")
                    ad_info = parse_ad_page(ad_url)

                    if ad_info:
                        seen_ads[ad_url]["last_checked"] = now.isoformat()

                        # Если дата обновления или цена изменилась
                        if (
                            ad_info.get("updated_date")
                            and ad_info.get("updated_date")
                            != ad_data.get("updated_date")
                        ) or (
                            ad_info.get("price")
                            and ad_info.get("price") != ad_data.get("price")
                        ):
                            print(f"[check_command] Объявление {ad_url} обновилось")
                            # Обновляем информацию
                            if ad_info.get("updated_date"):
                                seen_ads[ad_url]["updated_date"] = ad_info.get(
                                    "updated_date"
                                )
                            if ad_info.get("price"):
                                seen_ads[ad_url]["price"] = ad_info.get("price")
                            updated_ads.append(ad_url)
                    else:
                        print(
                            f"[check_command] Ошибка парсинга старого объявления {ad_url}"
                        )

        print(
            f"[check_command] Всего новых: {len(new_ads)}, обновленных: {len(updated_ads)}"
        )

        # Теперь формируем сообщения
        messages = []

        for ad_url in new_ads:
            try:
                ad_info = seen_ads[ad_url]
                message = format_ad_message(ad_info, "Новое объявление:")
                messages.append(message)
            except Exception as e:
                print(
                    f"[check_command] Ошибка при формировании сообщения для {ad_url}: {e}"
                )

        for ad_url in updated_ads:
            try:
                ad_info = seen_ads[ad_url]
                message = format_ad_message(ad_info, "Обновленное объявление:")
                messages.append(message)
            except Exception as e:
                print(
                    f"[check_command] Ошибка при формировании сообщения для {ad_url}: {e}"
                )

        # Группируем по 5 штук
        grouped_messages = [messages[i : i + 5] for i in range(0, len(messages), 5)]
        for group in grouped_messages:
            message = "\n\n".join(group)
            await context.bot.send_message(CHAT_ID, message)
            await asyncio.sleep(5)

        save_seen_ads(seen_ads)

    except Exception as e:
        print(f"[check_command] Ошибка: {e}")
        raise


# ======= Форматирование сообщения =======
def format_ad_message(ad_info, ad_type):
    # Проверяем наличие ключа 'url'
    url = ad_info.get(
        "url", "URL не доступен"
    )  # Если нет ссылки, выводим "URL не доступен"
    date_posted = ad_info.get("date_posted")
    updated_date = ad_info.get("updated_date")
    price = ad_info.get("price", "Не указана")  # Цена добавлена

    # Форматируем даты
    if date_posted:
        date_posted = date_posted.strftime("%d.%m.%Y, %H:%M")
    else:
        date_posted = "Не указана"

    if updated_date:
        updated_date = updated_date.strftime("%d.%m.%Y, %H:%M")
    else:
        updated_date = "Не указана"

    # Создаем текстовое сообщение
    message = (
        f"{ad_type}\n"
        f"{url}\n"
        f"Дата публикации: {date_posted}\n"
        f"Дата обновления: {updated_date}\n"
        f"Стоимость: {price}\n"
    )

    return message.strip()


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
