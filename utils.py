import os
from os.path import join, dirname
from datetime import datetime
from dotenv import load_dotenv
import requests
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import json

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

base_url = os.environ['BASE_URL_DEV']

class Time:
 def actual_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

 def actual_time_with_date():
    now = datetime.now()
    current_time = now.strftime("%d %B %H:%M:%S")
    return current_time

class Reports:
 def create_matched_report(runId, organization_name):
    report = open(f"./output/{runId}/report_matched.csv", "w")
    report.write(f'''Report for matched invoices of {organization_name}\nGenerated at: {Time.actual_time()}\n
    ,Bank Statement Lines,,,,Transactions,,,,\n
    Transaction No,Description Name,Ref,Spent,Received, ,Matched Contact,Ref,Spent,Received\n''')
    return report

 def create_summary_report(runId, organization_name):
    summary_report = open(f"./output/{runId}/summary_report.txt", "w")
    summary_report.write(f'REPORT ON ALL PROCESSED INVOICED FOR {organization_name}\nReport generated at: {Time.actual_time()}\n\n')
    return summary_report

 def create_not_matched_report(runId, organization_name):
    not_matched_report = open (f"./output/{runId}/report_not_matched.csv", "w")
    not_matched_report.write(f'Report for not matched invoices of {organization_name}\nGenerated at: {Time.actual_time()}\nTransaction No,Date,Description Name,Spent,Received\n')

    return not_matched_report

# Logging
class StatusLog:
    def send_live_log(runId, current_status):
        send_status  = {'data': f'{Time.actual_time()} {current_status}'}
        requests.post(f'{base_url}/bots/logs/{runId}', json=send_status)

    def send_error_message(runId, error_message):
        error = {'ErrorMessage' : str(error_message)}
        requests.post(f'{base_url}/bots/error/{runId}', json=error)

    def send_start_processing_log(runId):
        requests.post(f'{base_url}/bots/update-run-status/{runId}')

    def send_final_log(runId, json):
        requests.post(f'{base_url}/bots/logs/{runId}', json=json)

# Decrypting
def decrypt_user_password(user_password, secret):
    data = b64decode(user_password)
    bytes = PBKDF2(secret, "testsalt", 48, 128)
    iv = bytes[0:16]
    key = bytes[16:48]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_pass = cipher.decrypt(data).decode('utf-8')
    decrypted_pass = str(decrypted_pass)
    for n in decrypted_pass:
      if ord(n) <= 32:
        decrypted_pass = decrypted_pass.replace(n,'')
    return decrypted_pass

def get_otp(runId):
    otp = requests.get(f'{base_url}/bots/otp/{runId}').json()['data']['otp']
    return otp




