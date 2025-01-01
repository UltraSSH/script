import time
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Configurações do bot
BOT_TOKEN = "7661626757:AAFzcchrgW6I_Vt8UWqw7hcgG-eGNF-inkU"
CHAT_ID = 943180105
CHECK_INTERVAL = 120  # Intervalo em segundos (2 minutos)

# Lista para armazenar os sites a serem monitorados
monitored_sites = {}
last_status = {}

# Função de boas-vindas
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Olá! Sou seu bot de monitoramento de sites.\n"
        "Comandos disponíveis:\n"
        "/addsite <URL> - Adicionar um site para monitoramento\n"
        "/removesite <URL> - Remover um site do monitoramento\n"
        "/list - Listar sites monitorados\n"
        "/status - Verificar o status atual dos sites\n"
    )

# Função para adicionar um site para monitoramento
async def add_site(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        await update.message.reply_text("Uso: /addsite <URL>")
        return

    site = context.args[0]
    if site in monitored_sites:
        await update.message.reply_text(f"O site {site} já está sendo monitorado.")
    else:
        monitored_sites[site] = True
        last_status[site] = True
        await update.message.reply_text(f"Adicionado: {site} ao monitoramento.")

# Função para remover um site do monitoramento
async def remove_site(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        await update.message.reply_text("Uso: /removesite <URL>")
        return

    site = context.args[0]
    if site in monitored_sites:
        del monitored_sites[site]
        del last_status[site]
        await update.message.reply_text(f"Removido: {site} do monitoramento.")
    else:
        await update.message.reply_text(f"O site {site} não está sendo monitorado.")

# Função para listar os sites monitorados
async def list_sites(update: Update, context: CallbackContext):
    if not monitored_sites:
        await update.message.reply_text("Nenhum site está sendo monitorado no momento.")
    else:
        sites = "\n".join(monitored_sites.keys())
        await update.message.reply_text(f"Sites monitorados:\n{sites}")

# Função para verificar o status dos sites
async def status(update: Update, context: CallbackContext):
    if not monitored_sites:
        await update.message.reply_text("Nenhum site está sendo monitorado no momento.")
        return

    message = "Status dos sites:\n"
    for site in monitored_sites:
        try:
            response = requests.get(site, timeout=5)
            if response.status_code == 200:
                message += f"{site} - **Online**\n"
            else:
                message += f"{site} - **Offline**\n"
        except:
            message += f"{site} - **Offline**\n"

    await update.message.reply_text(message)

# Função que verifica se algum site ficou online ou offline
async def check_sites(context: CallbackContext):
    for site in list(monitored_sites.keys()):
        try:
            response = requests.get(site, timeout=5)
            current_status = response.status_code == 200
        except:
            current_status = False

        # Se o status mudou, envie uma notificação
        if current_status != last_status[site]:
            last_status[site] = current_status
            chat_id = context.job.context
            if current_status:
                await context.bot.send_message(chat_id=chat_id, text=f"O site {site} voltou a ficar **online**!")
            else:
                await context.bot.send_message(chat_id=chat_id, text=f"O site {site} ficou **offline**!")

# Função principal
def main():
    # Atualizado para a versão 20.x
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addsite", add_site))
    application.add_handler(CommandHandler("removesite", remove_site))
    application.add_handler(CommandHandler("list", list_sites))
    application.add_handler(CommandHandler("status", status))

    # Configura a tarefa de monitoramento
    application.job_queue.run_repeating(check_sites, interval=CHECK_INTERVAL, first=0, context=CHAT_ID)

    application.run_polling()

if __name__ == '__main__':
    main()
