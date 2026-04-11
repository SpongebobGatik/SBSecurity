import asyncio
import sys
import os
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import socket
from datetime import datetime, timedelta
import tempfile

last_request_time = {}
command_received_en = {}
command_received_de = {}
request_queue = asyncio.Queue()

async def process_queue():
    while True:
        try:
            username, job_coro = await request_queue.get()
            
            try:
                await job_coro
            except Exception as e:
                print(f"Ошибка при обработке запроса от {username}: {e}")
            finally:
                await asyncio.sleep(5)
                request_queue.task_done()
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Ошибка в очереди: {e}")
            await asyncio.sleep(1)

async def add_to_queue(update: Update, context: ContextTypes.DEFAULT_TYPE, job_coro):
    username = update.effective_user.username
    if username is None:
        username = update.effective_user.first_name
    
    await request_queue.put((username, job_coro))
    await update.message.reply_text('Ваш запрос добавлен в очередь.')

async def handle_encrypt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if command_received_en.get(user_id, False) == False:
        return
    
    if update.message.text:
        await add_to_queue(update, context, encrypt_text(update, context))
        command_received_en[user_id] = False
    elif update.message.document:
        await add_to_queue(update, context, encrypt_file(update, context))
        command_received_en[user_id] = False
    else:
        await update.message.reply_text('Пожалуйста, отправьте текстовый файл или текст для зашифровки.')

async def handle_decrypt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if command_received_de.get(user_id, False) == False:
        return
    
    if update.message.document.mime_type == 'application/zip':
        await add_to_queue(update, context, decrypt_zip(update, context))
        command_received_de[user_id] = False
    else:
        await update.message.reply_text('Пожалуйста, отправьте ZIP-архив для расшифровки.')
    
async def queue_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    queue_size = request_queue.qsize()
    response = f'Запросов в очереди: {queue_size}\n'
    if queue_size > 0:
        response += f'Примерное время ожидания: {queue_size * 5} секунд'
    await update.message.reply_text(response)

def send_to_server(message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(300)
            s.connect(('localhost', 10020))
            s.sendall(message.encode())

            response = b''
            while True:
                part = s.recv(4096)
                if not part:
                    break
                response += part
                if len(part) < 4096:
                    break

        return response
    except Exception as e:
        print(f"Ошибка соединения с сервером: {e}")
        raise

async def send_to_server_async(message):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, send_to_server, message)

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
    try:
        text = update.message.text
        response = await send_to_server_async(f'encrypt 0 {text}')
        
        with open('encrypted.zip', 'wb') as f:
            f.write(response)
        
        with open('encrypted.zip', 'rb') as f:
            await update.message.reply_document(document=f)
    except Exception as e:
        await update.message.reply_text(f'Ошибка при шифровании: {str(e)}')

async def encrypt_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        file = await update.message.document.get_file()
        
        if file.file_size <= 10 * 1024 * 1024:
            with tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False, suffix='.txt') as tmp:
                tmp_filename = tmp.name
                await file.download_to_drive(tmp_filename)
                tmp.seek(0)
                text = tmp.read()
            
            longest_line_length, line_count = analyze_text(text)
            if longest_line_length * line_count <= 100000:
                response = await send_to_server_async(f'encrypt 0 {text}')
                
                with open('encrypted.zip', 'wb') as f:
                    f.write(response)
                
                with open('encrypted.zip', 'rb') as f:
                    await update.message.reply_document(document=f)
            else:
                await update.message.reply_text(
                    'Произведение длины самой длинной строки на количество строк превышает 100000. '
                    'Пожалуйста, отправьте другой файл.'
                )
            
            # Удаляем временный файл
            os.unlink(tmp_filename)
        else:
            await update.message.reply_text(
                'Размер файла превышает 10 мб. Пожалуйста, отправьте файл меньшего размера.'
            )
    except Exception as e:
        await update.message.reply_text(f'Ошибка при обработке файла: {str(e)}')
        
async def decrypt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    now = datetime.now()

    if user_id in last_request_time:
        if now - last_request_time[user_id] < timedelta(minutes=15):
            await update.message.reply_text('Вы можете делать запрос только раз в 15 минут.')
            return

    last_request_time[user_id] = now
    command_received_de[user_id] = True
    command_received_en[user_id] = False
    await update.message.reply_text('Отправьте zip архив для расшифровки:')

async def decrypt_zip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        file = await update.message.document.get_file()
        
        if file.file_size <= 10 * 1024 * 1024:
            await file.download_to_drive('encrypted.zip')
            response = await send_to_server_async('decrypt 0')
            
            with open('decrypted.txt', 'wb') as f:
                f.write(response)
            
            with open('decrypted.txt', 'rb') as f:
                await update.message.reply_document(document=f)
        else:
            await update.message.reply_text(
                'Размер файла превышает 10 мб. Пожалуйста, отправьте файл меньшего размера.'
            )
    except Exception as e:
        await update.message.reply_text(f'Ошибка при расшифровке: {str(e)}')

def analyze_text(text):
    lines = text.split('\n')
    longest_line_length = max(len(line) for line in lines) if lines else 0
    line_count = len(lines)
    return longest_line_length, line_count

async def start_queue(app):
    queue_task = asyncio.create_task(process_queue())
    app.bot_data['queue_task'] = queue_task

async def stop_queue(app):
    if 'queue_task' in app.bot_data:
        app.bot_data['queue_task'].cancel()
        try:
            await app.bot_data['queue_task']
        except asyncio.CancelledError:
            pass

def main():
    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    
    if not TOKEN:
        print("Ошибка: переменная окружения TELEGRAM_TOKEN не установлена")
        sys.exit(1)
    
    proxy_url = os.environ.get('PROXY_URL')
    
    app_builder = Application.builder().token(TOKEN)
    
    if proxy_url:
        print(f"Используется прокси: {proxy_url}")
        app_builder = app_builder.proxy(proxy_url).get_updates_proxy(proxy_url)
    else:
        print("Прокси не используется, прямое подключение")
    
    application = app_builder.build()
    
    application.post_init = start_queue
    application.post_shutdown = stop_queue
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("encrypt", encrypt))
    application.add_handler(CommandHandler("decrypt", decrypt))
    application.add_handler(CommandHandler("queue", queue_status))
    application.add_handler(MessageHandler(filters.Document.MimeType("application/zip"), handle_decrypt))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_encrypt))
    application.add_handler(MessageHandler(filters.Document.MimeType("text/plain"), handle_encrypt))
    
    print("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()
