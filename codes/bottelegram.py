import asyncio
import sys
import os
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import socket
from datetime import datetime, timedelta
from queue import Queue
from threading import Thread
import time

last_request_time = {}
request_queue = Queue()
command_received_en = {}
command_received_de = {}

def process_queue():
    while True:
        job_tuple = request_queue.get()
        if job_tuple is None:
            break

        _, job = job_tuple

        job()

        time.sleep(5)


queue_thread = Thread(target=process_queue)
queue_thread.start()


async def add_to_queue(update: Update, context: ContextTypes.DEFAULT_TYPE, job):
    username = update.effective_user.username
    if username is None:
        username = update.effective_user.first_name
    request_queue.put((username, job))
    await update.message.reply_text('Ваш запрос добавлен в очередь.')

async def handle_encrypt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if command_received_en.get(user_id, False) == False:
        return
    
    if update.message.text:
        await add_to_queue(update, context, lambda: asyncio.run(encrypt_text(update, context)))
        command_received_en[user_id] = False
    elif update.message.document:
        await add_to_queue(update, context, lambda: asyncio.run(encrypt_file(update, context)))
        command_received_en[user_id] = False
    else:
        await update.message.reply_text('Пожалуйста, отправьте текстовый файл или текст для зашифровки.')

async def handle_decrypt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if command_received_de.get(user_id, False) == False:
        return
    
    if update.message.document.mime_type == 'application/zip':
        await add_to_queue(update, context, lambda: asyncio.run(decrypt_zip(update, context)))
        command_received_de[user_id] = False
    else:
        await update.message.reply_text('Пожалуйста, отправьте ZIP-архив для расшифровки.')
    
async def queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    queue_items = list(request_queue.queue)
    response = 'Список очереди:\n'
    for index, (username, _) in enumerate(queue_items, start=1):
        response += f'{index}. {username}\n'
    await update.message.reply_text(response)

def send_to_server(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 10020))
        s.sendall(message.encode())

        response = b''
        while True:
            part = s.recv(4096)
            response += part
            if len(part) < 4096:
                break

    return response

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_markdown_v2(
        fr'Привет, {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )

async def encrypt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    now = datetime.now()

    if user_id in last_request_time:
        if now - last_request_time[user_id] < timedelta(minutes=15):
            await update.message.reply_text('Вы можете делать запрос только раз в 15 минут.')
            return

    last_request_time[user_id] = now
    command_received_en[user_id] = True
    command_received_de[user_id] = False
    await update.message.reply_text('Введите текст для шифрования:')

async def encrypt_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    response = send_to_server(f'encrypt 0 {text}')
    
    with open('encrypted.zip', 'wb') as f:
        f.write(response)
    await update.message.reply_document(document=open('encrypted.zip', 'rb'))

async def encrypt_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    file = await update.message.document.get_file()
    
    if file.file_size <= 10 * 1024 * 1024:
        file_path = await file.download_to_drive()
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        longest_line_length, line_count = analyze_text(text)
        if longest_line_length * line_count <= 100000:
            response = send_to_server(f'encrypt 0 {text}')
            with open('encrypted.zip', 'wb') as f:
                f.write(response)
            await update.message.reply_document(document=open('encrypted.zip', 'rb'))
        else:
            await update.message.reply_text('Произведение длины самой длинной строки на количество строк превышает 100000. Пожалуйста, отправьте другой файл.')
    else:
        await update.message.reply_text('Размер файла превышает 10 мб. Пожалуйста, отправьте файл меньшего размера.')
        
async def decrypt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    now = datetime.now()

    if user_id in last_request_time:
        if now - last_request_time[user_id] < timedelta(minutes=1):
            await update.message.reply_text('Вы можете делать запрос только раз в 15 минут.')
            return

    last_request_time[user_id] = now
    command_received_de[user_id] = True
    command_received_en[user_id] = False
    await update.message.reply_text('Отправьте zip архив для расшифровки:')

async def decrypt_zip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    file = await update.message.document.get_file()
    
    if file.file_size <= 10 * 1024 * 1024:
        await file.download_to_drive('encrypted.zip')
        response = send_to_server('decrypt 0')
        with open('decrypted.txt', 'wb') as f:
            f.write(response)
        await update.message.reply_document(document=open('decrypted.txt', 'rb'))
    else:
        await update.message.reply_text('Размер файла превышает 10 мб. Пожалуйста, отправьте файл меньшего размера.')

def analyze_text(text):
    lines = text.split('\n')
    longest_line_length = max(len(line) for line in lines) if lines else 0
    line_count = len(lines)
    return longest_line_length, line_count

def main() -> None:
    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    if not TOKEN:
        print("Ошибка: переменная окружения TELEGRAM_TOKEN не установлена")
        sys.exit(1)
    
    proxy_url = os.environ.get('PROXY_URL')
    
    if proxy_url:
        print(f"Используется прокси: {proxy_url}")
        request_kwargs = {
            'proxy': proxy_url,
            'connect_timeout': 20.0,
            'read_timeout': 20.0,
        }
        req = HTTPXRequest(**request_kwargs)
        application = Application.builder().token(TOKEN).request(req).build()
    else:
        print("Прокси не используется, прямое подключение")
        application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("encrypt", encrypt))
    application.add_handler(CommandHandler("decrypt", decrypt))
    application.add_handler(CommandHandler("queue", queue))
    application.add_handler(MessageHandler(filters.Document.MimeType("application/zip"), handle_decrypt))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_encrypt))
    application.add_handler(MessageHandler(filters.Document.MimeType("text/plain"), handle_encrypt))
    application.run_polling()

if __name__ == '__main__':
    main()
