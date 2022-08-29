from posixpath import split
from dados_conta import BOT_TOKEN
import telebot
from telebot import formatting
import zabbix_data
from zabbix_graph import get_graph
from datetime import datetime, timedelta, date
import time
import threading
import re
import random
import os

saudacao = r'bom dia.*$|oi.*$|ola.*$|boa tarde.*$|boa noite.*$|olá.*$|oie.*$'
frases_evasivas = ['La pregunta ?', 'Não fui treinado pra isso',
                   'Se explique melhor', 'Experimente outra frase',
                   'Não sou tão inteligente assim',
                   'Você já experimentou perguntar ao google ?',
                   'Você fala coisas difíceis cara']

cadastros = []


bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)


def welcome(message):
    bot.send_message(
        message.chat.id, f'Iae {message.chat.first_name} muito doido, '
        f'tudo sussa ?\n O que você deseja ?')
    bot.send_message(message.chat.id,
                     formatting.format_text(
                         formatting.escape_markdown('Você pode pesquisar por'),
                         formatting.mbold(
                             '"hosts", "incidentes", "eventos" e "gráficos"...'),
                         separator=" "
                     ),
                     parse_mode='MarkdownV2')


def try_again(message):
    bot.send_message(
        message.chat.id, f'{message.chat.first_name} muito doido, '
        f'tente novamente !\n O que você deseja ?')
    bot.send_message(message.chat.id,
                     formatting.format_text(
                         formatting.escape_markdown('Você pode pesquisar por'),
                         formatting.mbold(
                             '"hosts", "incidentes", "eventos" e "gráficos"...'),
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
    hosts = filter_host(message)
    if not hosts:
        try_again(message)
    elif len(hosts) == 1:
        resultados = zabbix_data.eventos_ultimo_dia_host(hosts[0]['hostid'])
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
        msg = bot.send_message(message.chat.id,
                               f'Foi encontrado diversos host, escolha algum'
                               ' informando o id:')
        bot.register_next_step_handler(msg, view_event3)


def view_event3(message):
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
            try_again(message)
    else:
        bot.send_message(message.chat.id, 'É necessário informar o ID,'
                         ' Você informou um texto')
        try_again(message)


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
        return hosts

    else:
        bot.send_message(
            message.chat.id,
            f'Não foi encontrado nenhum host '
            f'com o termo informado')
        return


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


def view_graph(message):
    msg = bot.send_message(
        message.chat.id, f'Visualize os gráficos  do host desejado.\n'
        f'Informe um termo para pesquisar por hosts que'
        f' deseja consultar:')
    bot.register_next_step_handler(msg, view_graph2)


def view_graph2(message):
    hosts = filter_host(message)
    if not hosts:
        try_again(message)
    elif len(hosts) == 1:
        graficos = zabbix_data.get_graphs(hosts[0]['hostid'])
        for grafico in graficos:
            get_graph(grafico['graphid'])
            image = open('./imagem.png', 'rb')
            bot.send_photo(message.chat.id, image)
    else:
        msg = bot.send_message(message.chat.id,
                               f'Foi encontrado diversos host, escolha algum'
                               ' informando o id:')
        bot.register_next_step_handler(msg, view_graph3)


def view_graph3(message):
    if message.text.isdigit():
        graficos = zabbix_data.get_graphs(message.text)
        for grafico in graficos:
            get_graph(grafico['graphid'])
            image = open('./imagem.png', 'rb')
            bot.send_photo(message.chat.id, image)
    else:
        bot.send_message(message.chat.id, 'É necessário informar o ID,'
                         ' Você informou um texto')


@bot.message_handler(commands=['start', 'ajuda', 'help'])
def send_welcome(message):
    welcome(message)


def salvar_registro():
    arquivo = open('cadastro.txt', 'w')
    for cad in cadastros:
        arquivo.write(str(cad) + '\n')
    arquivo.close()


def carregar_registros():
    global cadastros
    if os.path.exists('cadastro.txt'):
        arquivo = open('cadastro.txt', 'r')
        for cad in arquivo.readlines():
            cadastros.append(int(cad.replace('\n', '')))


def registra(message):
    if message.chat.id in cadastros:
        bot.send_message(message.chat.id, 'Você já está inscrito')
        return

    cadastros.append(message.chat.id)
    salvar_registro()
    bot.send_message(message.chat.id, 'Cadastro realizado com sucesso !')


def envia_problemas():
    for cad in cadastros:
        problemas = zabbix_data.problemas_zabbix()
        for problema in problemas:
            problema = problema.split('@')
            bot.send_message(
                cad,
                formatting.format_text(
                    formatting.mbold(problema[0]),
                    formatting.munderline(problema[1]),
                    formatting.mcode(problema[2]),
                    separator=" "
                ),
                parse_mode='MarkdownV2')
    agendar_processamento()


def agendar_processamento():
    global sub_timer
    sub_timer = threading.Timer(43200.0, envia_problemas)
    sub_timer.start()



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

    elif re.match(r'^.*grafico.*$|^.*gráfico.*$', message.text,
                  re.IGNORECASE):
        view_graph(message)

    elif re.match(r'^.*cadastr.*$|^.*registr.*$', message.text,
                  re.IGNORECASE):
        registra(message)

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


def main():
    carregar_registros()
    agendar_processamento()

    while True:
        try:
            bot.infinity_polling()

        except Exception as e:
            print(f'Erro no telebot: {e}')
            bot.stop_polling()
            time.sleep(60)


if __name__ == '__main__':
    main()
