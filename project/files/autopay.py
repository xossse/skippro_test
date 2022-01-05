import logging

import requests

logging.basicConfig(level=logging.DEBUG, filename='./autopay.log', format='%(asctime)s %(levelname)s:%(message)s')
response = requests.get('https://easypayments.vip/api/chekPlanAndPay')
if response.status_code == 200:
    logging.debug(str(response.json()))
    print('ok')