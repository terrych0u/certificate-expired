#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import json
import requests
import socket
import ssl
import time


def webhook(message, max_retries=3, retry_delay=3):
    retries = 0

    headers = {
        "Content-Type": "application/json"
    }

    payload = json.dumps(message)

    while retries < max_retries:
        try:
            response = requests.post(url, data=payload, headers=headers)
            # 檢查請求是否成功，根據實際需求自行判斷
            if response.status_code == 200:
                print(response.text)
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error occurred: {e}")
            retries += 1
    
        # 等待指定的延遲時間
        time.sleep(retry_delay)

    return None



if __name__ == '__main__':

    alert_days = 30
    port = 443
    server_list = open( "list.txt", "r")
    url = ""


    for lists in server_list:
        # endpoint = lists.strip().split()[0]
        domain = lists.strip().split()[0]
        cdn = lists.strip().split()[1]

        try:
            # 連線到網站並獲取憑證
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
                s.connect((domain, port))
                cert = s.getpeercert()

            # 解析憑證的有效期
            cert_expiry_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            
            # 取得現在的日期和時間
            now = datetime.datetime.now()

            # 計算憑證的過期剩餘天數
            remaining_days = (cert_expiry_date - now).days

            if remaining_days < alert_days:
                # message = "%s certificate %s will expires in %s days \n" % (cdn, domain, remaining_days)
                message = {"msgtype": "text","text": {"content":"%s certificate %s will expires in %s days \n" % (cdn, domain, remaining_days)}}
            else:
                # message = "The certificate for %s on %s is still valid for %s days" % (domain, cdn, remaining_days)
                message = {"msgtype": "text","text": {"content":"The certificate for %s on %s is still valid for %s days" % (domain, cdn, remaining_days)}}
        
        except ssl.SSLError as e:
            print(f"An error occurred while checking the certificate: {e}")
        
        except socket.error as e:
            print(f"An error occurred while connecting to the domain: {e}")


        # print(message)
        if not message:
            continue
        else:
            webhook(message)
