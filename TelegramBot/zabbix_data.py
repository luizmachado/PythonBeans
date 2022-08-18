import time
from datetime import datetime
from pyzabbix.api import ZabbixAPI
from dados_conta import ZABBIX_SERVER, ZABBIX_API_TOKEN, ZABBIX_USER

zapi = ZabbixAPI(ZABBIX_SERVER)

# Logar na API Zabbix
zapi.login(ZABBIX_USER, api_token=ZABBIX_API_TOKEN)

# Função para obter histórico de determinado item

# Definir período
TIME_NOW = time.mktime(datetime.now().timetuple())
HOUR_AGO = TIME_NOW - 60 * 60 * 1  # 1 hora
DAY_AGO = TIME_NOW - 60 * 60 * 24  # 1 hora


def historico_ultima_hora(id_item):

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






def problemas_zabbix():

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
    unack_trigger_ids = [t["triggerid"] for t in unack_triggers]
    for t in triggers:
        t["unacknowledged"] = True if t["triggerid"] \
            in unack_trigger_ids else False

    # Retornar lista com as triggers ativas
    resultado = []
    for t in triggers:
        if int(t["value"]) == 1:
            # Resultado com marcador '@' pra posterior marcação
            resultado.append(
                "{} -@ {} @{}".format(
                    t["hosts"][0]["host"],
                    t["description"],
                    "(Não Reconhecido)" if t["unacknowledged"]
                    else "(Reconhecido)",
                )
            )
    return resultado

# Função para obter lista com hosts


def get_hosts():
    resultado = []
    hosts = zapi.host.get(output=['name'])
    for host in hosts:
        resultado.append(host)
    return resultado


if __name__ == '__main__':
    historico_ultima_hora_host(10460)
