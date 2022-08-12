from posixpath import split
from dados_conta import BOT_TOKEN
import telebot
from telebot import formatting
import zabbix_data
import re
import random

saudacao = r'bom dia.*$|oi.*$|ola.*$|boa tarde.*$|boa noite.*$|olá.*$|oie.*$'
frases_evasivas = ['La pregunta ?', 'Não fui treinado pra isso',
'Se explique melhor', 'Experimente outra frase',
'Não sou tão inteligente assim', 'Você já experimentou perguntar ao google ?',
'Você fala coisas difíceis cara']


bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

@bot.message_handler(commands=['start', 'ajuda'])
def send_welcome(message):
    bot.send_message(
            message.chat.id, f'Olá {message.chat.first_name} muito doido ! '
        f'Seja bem-vindo ao Robô do Integrado ao Zabbix.')


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if re.match(saudacao, message.text, re.IGNORECASE):
        bot.send_message(
                message.chat.id, f'Iae {message.chat.first_name} muito doido, '
            f'tudo sussa ?\n O que você deseja ?')
    elif re.match(r'^.*problema.*$|^.*incidente.*$', message.text, re.IGNORECASE):
        problemas=zabbix_data.problemas_zabbix()
        for problema in problemas:
            problema=problema.split('@')
            bot.send_message(
                message.chat.id,
                formatting.format_text(
                    formatting.mbold(problema[0]),
                    formatting.munderline(problema[1]),
                    formatting.mcode(problema[2]),
                    separator=" "
                ),
                parse_mode='MarkdownV2')
    # Easter Egg
    elif re.match(r'^.*teste.*$', message.text, re.IGNORECASE):
        bot.send_message(
                message.chat.id, "Não me analise, não estou aqui para ser testado.")
    elif re.match(r'qui nada', message.text, re.IGNORECASE):
        bot.send_message(
                message.chat.id, "Quem nada é peixe, quem pula é sapo.")
    else:
        bot.reply_to(message, random.choice(frases_evasivas))


bot.infinity_polling()
