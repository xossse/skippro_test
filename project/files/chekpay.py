import logging

import requests

logging.basicConfig(level=logging.DEBUG, filename='./checkpay.log', format='%(asctime)s %(levelname)s:%(message)s')
response = requests.get('https://easypayments.vip/request/CheckPayCentApp')
if response.status_code == 200:
    logging.debug(str(response.json()))
    print('ok')