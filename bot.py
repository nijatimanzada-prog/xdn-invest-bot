import os
import time
import requests
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    requests.post(
        f"{BASE_URL}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text[:4000]
        },
        timeout=20
    )

def ask_gpt(text):
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "Ты инвестиционный аналитик Nijat. Анализируй акции, IPO, earnings, новости, катализаторы, вход, цель, стоп и стоит ли покупать сейчас. Отвечай по-русски, практично и конкретно."
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )
    return response.choices[0].message.content

def main():
    offset = None
    print("Bot started")

    while True:
        try:
            params = {"timeout": 30}
            if offset is not None:
                params["offset"] = offset

            response = requests.get(
                f"{BASE_URL}/getUpdates",
                params=params,
                timeout=40
            )

            data = response.json()

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                message = update.get("message", {})
                chat = message.get("chat", {})
                chat_id = chat.get("id")
                text = message.get("text")

                if chat_id and text:
                    send_message(chat_id, "Принял. Анализирую...")
                    answer = ask_gpt(text)
                    send_message(chat_id, answer)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()
