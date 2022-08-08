import cx_Oracle
from pyzabbix import ZabbixMetric, ZabbixSender
from dados_conta import pwd_orcl, srv_zabbix, port_zabbix, srv_db

hostzabbix = 'contingencia'
dict_pend_cont = list()
dict_envionfe = list()
metrics_cont = []
metrics_envionfe = []
translation = {}

# Iniciar Conexão com banco
con = cx_Oracle.connect(f'SGACONSULTA/{pwd_orcl}@{srv_db}/orcl')


# Executar consulta para verificar registros pendentes de replicacao
cur = con.cursor()
cur.execute("SELECT EMPSIGLA, COUNT (*) QUANT_PENDENCIAS FROM SYSDBA.CENTSERVIDOR "
            "JOIN SYSDBA.EMPRESA ON CSBASE = EMPCOD GROUP BY EMPSIGLA")

# Criar dicionário com resultados
for result in cur:
    dict_pend_cont.append({result[0]: result[1]})
    print(result)

if not any('MINERAX' in d for d in dict_pend_cont):
    dict_pend_cont.append({'MINERAX': 0})

if not any('CALTINS' in d for d in dict_pend_cont):
    dict_pend_cont.append({'CALTINS': 0})

if not any('NATICAL' in d for d in dict_pend_cont):
    dict_pend_cont.append({'NATICAL': 0})

if not any('SUPERCAL' in d for d in dict_pend_cont):
    dict_pend_cont.append({'SUPERCAL': 0})

if not any('IMPERIO' in d for d in dict_pend_cont):
    dict_pend_cont.append({'IMPERIO': 0})

if not any('FORMACAL' in d for d in dict_pend_cont):
    dict_pend_cont.append({'FORMACAL': 0})

if not any('NOBRETINS' in d for d in dict_pend_cont):
    dict_pend_cont.append({'NOBRETINS': 0})

# Encerrar conexão da consulta
cur.close()

# Executar consulta para verificar notas pendentes de envio por email
cur = con.cursor()
cur.execute("SELECT COUNT(*) C FROM sysdba.DOCUMENTOELETRONICO "
            "JOIN sysdba.NOTAFISCAL ON NFCOD = DEREF "
            "WHERE DESIT = 3 "
            "AND DETIPO = 0 "
            "AND DEDISPPREVISAO > TO_DATE('30/12/1899', 'dd/mm/yyyy') "
            "AND DEDISPPREVISAO <=  SYSTIMESTAMP "
            "AND DEDISPDATA <= TO_DATE('30/12/1899', 'dd/mm/yyyy') "
            "AND NFSIT = 1")
for result in cur:
    dict_envionfe = result

# Encerrar conexão da consulta
cur.close()

# Encerrar conexão da conexao
con.close()

# Criar objeto ZabbixMetric com resultado do servidor Contingencia
for pend in dict_pend_cont:
    for emp, qtd in pend.items():
        m = ZabbixMetric(hostzabbix, emp, qtd)
        metrics_cont.append(m)

# Criar objeto ZabbixMetric com resultado do envio de NF por email
metrics_envionfe.append(ZabbixMetric('envio_emails_sga', 'ENVIONFE', dict_envionfe[0]))

# Enviar para Zabbix Trap
zbx = ZabbixSender(zabbix_server=srv_zabbix, zabbix_port=port_zabbix)
zbx.send(metrics_cont)
zbx.send(metrics_envionfe)

