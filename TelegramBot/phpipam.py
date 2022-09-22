import requests
import json
from dados_conta import PHPIPAM_TOKEN, PHPIPAM_URL


response = requests.get(PHPIPAM_URL, headers={
    "token": PHPIPAM_TOKEN,
})

response = (response.json())
print(json.dumps(response, indent=4, ensure_ascii=False))
