import requests
import logging
from datetime import datetime

# CONFIGURACIÓN
TELEGRAM_API_TOKEN = "7779030184:AAFUrTNBmC_KeJ27nfVx_Cg-aUkOylMct64"
TELEGRAM_CHAT_ID = "7925857119"
TARGET_URL = "https://spotlight-trigger-monitors-professionals.trycloudflare.com/"
LOG_FILE = "monitor.log"

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def send_telegram_notification(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        r = requests.post(url, json=data, timeout=10)
        return r.ok
    except Exception as e:
        logging.error(f"Error al enviar notificación: {e}")
        return False

def monitor():
    try:
        r = requests.get(TARGET_URL, timeout=10)
        current_status = r.status_code == 200
    except requests.RequestException:
        current_status = False

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not current_status:
        msg = (
            f"❌ <b>Web caída</b>\n"
            f"🕒 {now}\n"
            f"🔗 {TARGET_URL}"
        )
        send_telegram_notification(msg)
        logging.warning(msg)

if __name__ == "__main__":
    monitor()
