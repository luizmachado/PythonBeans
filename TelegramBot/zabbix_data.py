import time
import pprint
from datetime import datetime
from pyzabbix.api import ZabbixAPI
from dados_conta import ZABBIX_SERVER, ZABBIX_API_TOKEN, ZABBIX_USER

zapi = ZabbixAPI(ZABBIX_SERVER)

# Logar na API Zabbix
zapi.login(ZABBIX_USER, api_token=ZABBIX_API_TOKEN)


# Definir período
TIME_NOW = time.mktime(datetime.now().timetuple())
HOUR_AGO = TIME_NOW - 60 * 60 * 1  # 1 hora
DAY_AGO = TIME_NOW - 60 * 60 * 24  # 1 dia


def historico_ultima_hora(id_item):
    '''Função para obter histórico de determinado item'''

    resultado = []

    # Obter histórico com dados inteiros
    history = zapi.history.get(
        itemids=[id_item],
        time_from=int(HOUR_AGO),
        time_till=int(TIME_NOW),
        output="extend",
        limit="5000",
    )

    # Se não for encontrado dados inteiros, obter dados ponto flutuante
    if not len(history):
        history = zapi.history.get(
            itemids=[id_item],
            time_from=HOUR_AGO,
            time_till=TIME_NOW,
            output="extend",
            limit="5000",
            history=0,
        )

    # Printar cada ponto de dados
    for point in history:
        resultado.append(
            "{}: {}".format(
                datetime.fromtimestamp(int(point["clock"])).strftime("%x %X"),
                point["value"],
            )
        )
    zapi.logout()
    return resultado


def historico_ultima_hora_host(id_host):
    '''Função para obter histórico de determinado host'''

    resultado = []

    # Obter histórico com dados inteiros
    history = zapi.history.get(
        hostids=[id_host],
        time_from=int(HOUR_AGO),
        time_till=int(TIME_NOW),
        output="extend",
        limit="5000",
    )

    # Se não for encontrado dados inteiros, obter dados ponto flutuante
    if not len(history):
        history = zapi.history.get(
            hostids=[id_host],
            time_from=HOUR_AGO,
            time_till=TIME_NOW,
            output="extend",
            limit="5000",
            history=0,
        )

    # Printar cada ponto de dados
    for point in history:
        resultado.append(point)

    return resultado


def eventos_ultimo_dia_host(id_host):
    '''Função para obter eventos de determinado host'''

    resultado = []

    events = zapi.event.get(
        hostids=[id_host],
        time_from=DAY_AGO,
        time_till=TIME_NOW,
        sortfield='clock',
    )
    for event in events:
        resultado.append(
            "{} - Problema: {} - @ {}".format(
                datetime.fromtimestamp(
                    int(event["clock"])).strftime("%x %X"),
                event["name"],
                "(Reconhecido)" if event["acknowledged"] == '1'
                else "(Não Reconhecido)",
            )
        )

    return resultado


def problemas_zabbix():
    '''Função para descoberta de problemas'''

    resultado = []

    # Obter lista com todos os problemas
    triggers = zapi.trigger.get(
        only_true=1,
        skipDependent=1,
        monitored=1,
        active=1,
        output="extend",
        expandDescription=1,
        selectHosts=["host"],)

    # Obter lista de todos os problemas não reconhecidos
    unack_triggers = zapi.trigger.get(
        only_true=1,
        skipDependent=1,
        monitored=1,
        active=1,
        output="extend",
        expandDescription=1,
        selectHosts=["host"],
        withLastEventUnacknowledged=1,
    )
    unack_trigger_ids = [trigger["triggerid"] for trigger in unack_triggers]
    for trigger in triggers:
        trigger["unacknowledged"] = True if trigger["triggerid"] \
            in unack_trigger_ids else False

    # Retornar lista com as triggers ativas
    for trigger in triggers:
        if int(trigger["value"]) == 1:
            # Resultado com marcador '@' pra posterior marcação
            resultado.append(
                "{} -@ {} @{}".format(
                    trigger["hosts"][0]["host"],
                    trigger["description"],
                    "(Não Reconhecido)" if trigger["unacknowledged"]
                    else "(Reconhecido)",
                )
            )
    return resultado


def get_hosts():
    '''Função para obter lista com hosts'''
    resultado = []
    hosts = zapi.host.get(output=['name'])
    for host in hosts:
        resultado.append(host)
    return resultado


if __name__ == '__main__':
    problemas = problemas_zabbix()
    for evento in problemas:
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(evento)
