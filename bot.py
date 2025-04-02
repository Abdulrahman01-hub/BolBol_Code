import logging
import random
import requests
import openai
from datetime import datetime
from gtts import gTTS
import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from time import sleep

# Logger ayarları
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# API Anahtarları
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
WEATHER_API_KEY = "YOUR_WEATHER_API_KEY"
TELEGRAM_API_KEY = "7766071502:AAE5sJH1bnO3AWhdCOl1YXH9kq4AOUpLwtk"

# Scheduler for reminders
scheduler = AsyncIOScheduler()

# ChatGPT destekli sohbet
async def chatgpt_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}],
        api_key=OPENAI_API_KEY
    )
    reply = response["choices"][0]["message"]["content"]
    await update.message.reply_text(reply)

# Hava Durumu Fonksiyonu
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Şehir adı giriniz. Örn: /weather Istanbul")
        return
    city = " ".join(context.args)
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&lang=tr"
    response = requests.get(url).json()
    if "error" in response:
        await update.message.reply_text("Şehir bulunamadı, lütfen tekrar deneyin.")
        return
    weather_info = response["current"]
    msg = f"🌍 **{city}**\n🌡️ Sıcaklık: {weather_info['temp_c']}°C\n🌪️ {weather_info['condition']['text']}\n💨 Rüzgar: {weather_info['wind_kph']} km/s"
    await update.message.reply_text(msg)

# Sesli Yanıt Fonksiyonu
async def speak(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = " ".join(context.args) if context.args else "Merhaba! Ben Jarwiz."
    tts = gTTS(text, lang="tr")
    tts.save("output.mp3")
    await update.message.reply_audio(audio=open("output.mp3", "rb"))
    os.remove("output.mp3")

# Tarih ve Saat
async def datetime_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await update.message.reply_text(f"Anlık tarih ve saat: {now}")

# Rastgele Şaka
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    jokes = [
        "Bilgisayar neden soğuktur? Çünkü fanı var! 😂",
        "Kod yazan hayalet nedir? Bug! 👻",
        "Python neden yılan gibi kıvrılır? Çünkü esnek bir dil! 🐍",
    ]
    await update.message.reply_text(random.choice(jokes))

# Trivia Soruları
async def trivia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    trivia_questions = [
        {"question": "En hızlı hayvan nedir?", "answer": "Çita"},
        {"question": "Dünyanın en büyük okyanusu hangisidir?", "answer": "Pasifik Okyanusu"}
    ]
    trivia_question = random.choice(trivia_questions)
    await update.message.reply_text(f"Soru: {trivia_question['question']}")
    await update.message.reply_text(f"Cevap: {trivia_question['answer']}")

# Kullanıcı Bilgisi
async def user_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    await update.message.reply_text(f"Adınız: {user.first_name} {user.last_name}\nKullanıcı Adı: @{user.username}\nKullanıcı ID: {user.id}")

# Kullanıcıya Özel Hatırlatıcı
async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("Lütfen bir zaman ve hatırlatıcı mesajı girin. Örn: /reminder 10 'Toplantı var'")
        return
    time = int(context.args[0]) * 60  # Dakika cinsinden
    reminder_message = " ".join(context.args[1:])
    
    def send_reminder():
        update.message.reply_text(f"Hatırlatma: {reminder_message}")
    
    scheduler.add_job(send_reminder, 'interval', minutes=time)
    scheduler.start()
    await update.message.reply_text(f"{time} dakika sonra hatırlatıcı ayarlandı!")

# Anket
async def poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = " ".join(context.args) if context.args else "Hangi renk daha güzel?"
    options = ["Kırmızı", "Mavi", "Yeşil", "Sarı"]
    poll_msg = await update.message.reply_poll(question=question, options=options, is_anonymous=False)

# Zamanlayıcı Fonksiyonu
async def start_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Lütfen bir süre girin. Örn: /timer 10")
        return
    time_in_seconds = int(context.args[0])  # Dakika yerine saniye cinsinden
    await update.message.reply_text(f"{time_in_seconds} saniye sayılmaya başlıyor!")
    sleep(time_in_seconds)
    await update.message.reply_text(f"{time_in_seconds} saniye geçti!")

# Komutlar Listesi
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/start - Botu başlatır\n"
        "/help - Yardım mesajı\n"
        "/weather [şehir] - Hava durumu\n"
        "/joke - Rastgele şaka\n"
        "/datetime - Saat ve tarih\n"
        "/speak [metin] - Sesli mesaj\n"
        "/reminder [dakika] [mesaj] - Hatırlatıcı ayarlar\n"
        "/poll [soru] - Anket başlat\n"
        "/timer [saniye] - Zamanlayıcı başlat\n"
        "Mesaj göndererek yapay zeka ile sohbet edebilirsiniz!"
    )

# Botu Başlat
def main() -> None:
    application = Application.builder().token(TELEGRAM_API_KEY).build()
    application.add_handler(CommandHandler("start", help_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("weather", weather))
    application.add_handler(CommandHandler("joke", joke))
    application.add_handler(CommandHandler("datetime", datetime_command))
    application.add_handler(CommandHandler("speak", speak))
    application.add_handler(CommandHandler("reminder", set_reminder))
    application.add_handler(CommandHandler("poll", poll))
    application.add_handler(CommandHandler("timer", start_timer))
    application.add_handler(CommandHandler("user_info", user_info))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatgpt_response))
    logger.info("Bot başlatılıyor...")
    application.run_polling()

if __name__ == "__main__":
    main()
