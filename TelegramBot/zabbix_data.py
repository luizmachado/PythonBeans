import time
from datetime import datetime
from pyzabbix.api import ZabbixAPI
from dados_conta import ZABBIX_SERVER, ZABBIX_API_TOKEN, ZABBIX_USER

zapi = ZabbixAPI(ZABBIX_SERVER)

# Logar na API Zabbix 
zapi.login(ZABBIX_USER, api_token=ZABBIX_API_TOKEN)


# Função para obter histórico de determinado item
def historico_ultima_hora(id_item):
    # Definir intervalo de tempo
    time_till = time.mktime(datetime.now().timetuple())
    time_from = time_till - 60 * 60 * 1  # 1 hora

    # Obter histórico com dados inteiros
    history = zapi.history.get(
        itemids=[id_item],
        time_from=int(time_from),
        time_till=int(time_till),
        output="extend",
        limit="5000",
    )

    # Se não for encontrado dados inteiros, obter dados ponto flutuante
    if not len(history):
        history = zapi.history.get(
            itemids=[id_item],
            time_from=time_from,
            time_till=time_till,
            output="extend",
            limit="5000",
            history=0,
        )

    # Printar cada ponto de dados
    for point in history:
        print(
            "{}: {}".format(
                datetime.fromtimestamp(int(point["clock"])).strftime("%x %X"),
                point["value"],
            )
        )
    return

# Função para descoberta de problemas
def problemas_zabbix():
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
        t["unacknowledged"] = True if t["triggerid"] in unack_trigger_ids else False

    # Retornar lista com as triggers ativas
    resultado = []
    for t in triggers:
        if int(t["value"]) == 1:
            # Resultado com marcador '@' pra posterior marcação
            resultado.append(
                "{} -@ {} @{}".format(
                    t["hosts"][0]["host"],
                    t["description"],
                    "(Não Reconhecido)" if t["unacknowledged"] else "(Reconhecido)",
                )
            )
    return resultado


if __name__ == '__main__':
    problemas = problemas_zabbix()
    for problema in problemas:
        print(problema)
