import requests
import time
from datetime import datetime
import logging
import socket

# ===== CONFIGURACIÓN =====
TELEGRAM_API_TOKEN = "7779030184:AAFUrTNBmC_KeJ27nfVx_Cg-aUkOylMct64"
TELEGRAM_CHAT_ID = "7925857119"
TARGET_URL = "https://spotlight-trigger-monitors-professionals.trycloudflare.com/"
CHECK_INTERVAL = 300  # segundos = 5 minutos
LOG_FILE = "internet_monitor.log"

# ===== LOGGING =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# ===== FUNCIONES =====
def get_network_info():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
        return ip_local
    except Exception as e:
        logging.error(f"Error al obtener IP local: {e}")
        return "Desconocida"

def check_connection():
    try:
        response = requests.get(TARGET_URL, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logging.warning(f"Error al conectar: {e}")
        return False

def send_telegram_notification(message):
    endpoints = [
        "https://api.telegram.org",
        "https://api1.telegram.org",
        "https://api2.telegram.org"
    ]
    for endpoint in endpoints:
        try:
            response = requests.post(
                f"{endpoint}/bot{TELEGRAM_API_TOKEN}/sendMessage",
                json={
                    'chat_id': TELEGRAM_CHAT_ID,
                    'text': message,
                    'parse_mode': 'HTML'
                },
                timeout=10
            )
            if response.json().get('ok'):
                return True
        except Exception as e:
            logging.warning(f"Error con endpoint {endpoint}: {str(e)[:100]}")
    return False

# ===== LÓGICA PRINCIPAL =====
def main():
    ip_local = get_network_info()
    last_status = None

    start_msg = (
        f"🟢 <b>Monitor iniciado</b>\n"
        f"🔗 URL: {TARGET_URL}\n"
        f"📡 IP Local: <code>{ip_local}</code>\n"
        f"⏱ Frecuencia: {CHECK_INTERVAL // 60} minutos"
    )
    send_telegram_notification(start_msg)
    logging.info(start_msg)

    while True:
        current_status = check_connection()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if last_status is not None and current_status != last_status:
            if not current_status:
                msg = (
                    f"❌ <b>Web caída</b>\n"
                    f"🕒 Hora: {now}\n"
                    f"🔗 {TARGET_URL}\n"
                    f"📍 IP Local: <code>{ip_local}</code>"
                )
            else:
                msg = (
                    f"✅ <b>Web recuperada</b>\n"
                    f"🕒 Hora: {now}\n"
                    f"🔗 {TARGET_URL}"
                )
            send_telegram_notification(msg)
            logging.info(msg)

        last_status = current_status
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("🔴 Monitor detenido manualmente")
    except Exception as e:
        error_msg = f"⚠️ Error Crítico: {str(e)[:200]}"
        send_telegram_notification(error_msg)
        logging.critical(error_msg)


