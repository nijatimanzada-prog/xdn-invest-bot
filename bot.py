import os
import time
import requests
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("BOT_TOKEN exists:", bool(BOT_TOKEN), flush=True)
print("OPENAI_API_KEY exists:", bool(OPENAI_API_KEY), flush=True)

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN is missing")

if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY is missing")

client = OpenAI(api_key=OPENAI_API_KEY)
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    r = requests.post(
        f"{BASE_URL}/sendMessage",
        json={"chat_id": chat_id, "text": text[:4000]},
        timeout=20
    )
    print("sendMessage:", r.status_code, r.text[:200], flush=True)

def ask_gpt(text):
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "Ты инвестиционный аналитик Nijat. Анализируй акции, IPO, earnings, новости, катализаторы, вход, цель, стоп и стоит ли покупать сейчас. Отвечай по-русски, практично и конкретно."
            },
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

def main():
    print("Bot started", flush=True)

    me = requests.get(f"{BASE_URL}/getMe", timeout=20)
    print("getMe:", me.status_code, me.text, flush=True)

    offset = None

    while True:
        try:
            params = {"timeout": 30}
            if offset is not None:
                params["offset"] = offset

            r = requests.get(f"{BASE_URL}/getUpdates", params=params, timeout=40)
            print("getUpdates:", r.status_code, r.text[:300], flush=True)

            data = r.json()

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                text = message.get("text")

                print("MESSAGE:", chat_id, text, flush=True)

                if chat_id and text:
                    if text == "/start":
                        send_message(chat_id, "Бот работает. Напиши тикер или вопрос по рынку.")
                    else:
                        send_message(chat_id, "Принял. Анализирую...")
                        answer = ask_gpt(text)
                        send_message(chat_id, answer)

        except Exception as e:
            print("ERROR:", repr(e), flush=True)
            time.sleep(5)

if __name__ == "__main__":
    main()
