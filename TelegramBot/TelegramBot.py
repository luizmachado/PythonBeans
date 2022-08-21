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
                   'Não sou tão inteligente assim',
                   'Você já experimentou perguntar ao google ?',
                   'Você fala coisas difíceis cara']


bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)


def welcome(message):
    bot.send_message(
        message.chat.id, f'Iae {message.chat.first_name} muito doido, '
        f'tudo sussa ?\n O que você deseja ?')
    bot.send_message(message.chat.id,
                     formatting.format_text(
                         formatting.escape_markdown('Você pode pesquisar por'),
                         formatting.mbold('"hosts", "incidentes" e "eventos"'),
                         formatting.escape_markdown('sinta-se à vontade.'),
                         separator=" "
                     ),
                     parse_mode='MarkdownV2')


def view_events_intro(message):
    msg = bot.send_message(
        message.chat.id, f'Consulta de eventos nas últimas 24hs\n'
        f'Informe o id do host que'
        f' deseja consultar:')
    bot.register_next_step_handler(msg, view_event2)


def view_event2(message):
    if message.text.isdigit():
        resultados = zabbix_data.eventos_ultimo_dia_host(message.text)
        if resultados:
            for resultado in resultados:
                resultado = resultado.split('@')
                bot.send_message(
                    message.chat.id,
                    formatting.format_text(
                        formatting.mbold(resultado[0]),
                        formatting.mcode(resultado[1]),
                        separator=''
                    ),
                    parse_mode='MarkdownV2')
        else:
            bot.send_message(
                message.chat.id,
                f'Não foi encontrado nenhum evento '
                f'recente para o host informado.')
    else:
        bot.send_message(message.chat.id, 'É necessário informar o ID,'
                         ' Você informou um texto')


def filter_host(message):
    hosts = zabbix_data.get_hosts(message.text)
    if hosts:
        for host in hosts:
            bot.send_message(
                message.chat.id,
                formatting.format_text(
                    formatting.mbold(host['hostid']),
                    formatting.mcode(host['name']),
                    separator=" "
                ),
                parse_mode='MarkdownV2')
    else:
        bot.send_message(
            message.chat.id,
            f'Não foi encontrado nenhum host '
            f'com o termo informado')



def view_problems(message):
    problemas = zabbix_data.problemas_zabbix()
    for problema in problemas:
        problema = problema.split('@')
        bot.send_message(
            message.chat.id,
            formatting.format_text(
                formatting.mbold(problema[0]),
                formatting.munderline(problema[1]),
                formatting.mcode(problema[2]),
                separator=" "
            ),
            parse_mode='MarkdownV2')


@bot.message_handler(commands=['start', 'ajuda', 'help'])
def send_welcome(message):
    welcome(message)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if re.match(saudacao, message.text, re.IGNORECASE):
        welcome(message)

    elif re.match(r'^.*problema.*$|^.*incidente.*$', message.text,
                  re.IGNORECASE):
        view_problems(message)

    elif re.match(r'^.*host.*$|^.*equipamento.*$', message.text,
                  re.IGNORECASE):
        msg = bot.send_message(message.chat.id, 'Informe algum valor para'
                               ' filtrar hosts')
        bot.register_next_step_handler(msg, filter_host)

    elif re.match(r'^.*evento.*$', message.text,
                  re.IGNORECASE):
        view_events_intro(message)

    # Easter Egg
    elif re.match(r'^.*teste.*$', message.text, re.IGNORECASE):
        bot.send_message(
            message.chat.id,
            "Não me analise, não estou aqui para ser testado.")
    elif re.match(r'qui nada', message.text, re.IGNORECASE):
        bot.send_message(
            message.chat.id, "Quem nada é peixe, quem pula é sapo.")
    else:
        bot.reply_to(message, random.choice(frases_evasivas))


bot.infinity_polling()
