import os
from time import sleep
from dados_conta import ZABBIX_SERVER, ZABBIX_USER, ZABBIX_PWD


def get_graph(graph_id):
    login_cmd = f'wget  -q -O /dev/null --save-cookies=./cookies_file --keep-session-cookies "{ZABBIX_SERVER}/index.php?login=1&form=1&name={ZABBIX_USER}&password={ZABBIX_PWD}&enter=ENTER"'
    graph_cmd = f'wget --post-data="" -O ./imagem.png --load-cookies=./cookies_file "http://192.168.5.22/zabbix/chart2.php?graphid={graph_id}&from=now-7d&to=now"'
    print(graph_cmd)
    os.system(login_cmd)
    sleep(3)
    os.system(graph_cmd)
    return


if __name__ == '__main__':
    get_graph('2926')



#wget  quiet --save-cookies=./arquivo_cookie --keep-session-cookies 'http://192.168.5.22/zabbix/index.php?login=1&form=1&name=Admin&password=Ch@D0$t0mdt105&enter=ENTER'
#wget --post-data='' -O ./imagem.png --load-cookies=./arquivo_cookie "http://192.168.5.22/zabbix/chart2.php?graphid=2926&from=now-7d&to=now"
