# from RPA.Robocorp.Vault import Vault
from os.path import join, dirname
from RPA.Browser.Selenium import Selenium
# from RPA.Robocorp.WorkItems import UNDEFINED, WorkItems
import os
import time
import json
import dotenv
import requests
import sys
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import re
from dotenv import load_dotenv
from datetime import datetime
import subprocess

def actual_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

def actual_time_with_date():
    now = datetime.now()
    current_time = now.strftime("%d %B %H:%M:%S")
    return current_time

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
# sec = dotenv.get_key('SECRET')

browser = Selenium()

received = sys.argv[1]
received = json.loads(received)

error_status = os.environ['ERRORS_SEND_URL']
status_sender_url = os.environ['URL_FOR_LOGS']
otp_get_url = os.environ['OTP_GET_URL']
url_temp_send_files = os.environ['URL_FOR_UPLOAD']

# robocorp_webhook = 'https://api-dev.gdeeto.com/bots/webhook'
# Variables
url = 'https://login.xero.com/identity/user/login'
user_name = received['userName'] #items.get_work_item_variable('userName')
user_password = received['userPassword'] #items.get_work_item_variable('userPassword')
organization_name =  received['organizationName'] #items.get_work_item_variable('organizationName')
phrase_for_comment = received['commentPhrase'] #items.get_work_item_variable('commentPhrase')
phrase_if_error_exist = received['errorPhrase'] #items.get_work_item_variable('errorPhrase')
phrase_for_cheking_rule = 'The rule on this transaction need additional check by operator.'
bank_quantity = received['bankQuantity'] #items.get_work_item_variable('bankQuantity')
base_url_link_organization = 'https://go.xero.com/OrganisationLogin/?shortCode='
shortCode_link = received['shortCode'] #items.get_work_item_variable('shortCode')
company_name = received['companyName'] #items.get_work_item_variable('companyName')
organizationId = received['organizationId'] #items.get_work_item_variable('organizationId')
runId = received['runId'] #items.get_work_item_variable('runId')
secret = os.environ['SECRET'] #secrets.get_secret('secret_key')

# Left/right column selectors (Company Name, Spent, Received)
left_company_name = '(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]/../../div//*[@class="details"]/span[2]'
left_ref_field = '(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]/../../div//*[@class="details"]/span[3]'
left_amount_spent = '(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]/../../div//*[@class="amount spent set"]'
left_amount_received = '(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]/../../div//*[@class="amount received set"]'

right_compamy_name = '(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]/../..//*[@class="statement matched"]//*[@class="details"]/span[2]'
right_ref_field = '(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]/../..//*[@class="statement matched"]//*[@class="details"]/span[3]'
right_amount_spent = '(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]/../../div//*[@class="amount set"]'
right_amount_received = '(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]/../../div//*[@class="amount set"]'

# Counters for report
transaction_counter = 1
comment_count = 1
rule_transactions = 0
totally_reconciled = ''
statusReconcile = ''

os.makedirs(f'./output/{runId}', exist_ok=True)

# directory = os.path.dirname(f'./output/{runId}')
# if not os.path.exists(directory):
#     os.mkdir(f'./output/{runId}')

report = open(f"./output/{runId}/report_matched.csv", "w")
report.write(f'''Report for not matched invoices of {organization_name}\nGenerated at: {actual_time_with_date()}\n
,Bank Statement Lines,,,,Transactions,,,,\n
Transaction No,Description Name,Ref,Spent,Received, ,Matched Contact,Ref,Spent,Received\n''')

summary_report = open(f"./output/{runId}/summary_report.txt", "w")
summary_report.write(f'REPORT ON ALL PROCESSED INVOICED FOR {organization_name}\nReport generated at: {actual_time_with_date()}\n\n')

not_matched_report = open (f"./output/{runId}/report_not_matched.csv", "w")
not_matched_report.write(f'Report for not matched invoices of {organization_name}\nGenerated at: {actual_time_with_date()}\nTransaction No,Date,Description Name,Spent,Received\n')

def started_process_report():
    requests.post(f'https://api-dev.gdeeto.com/bots/update-run-status/{runId}')

started_process_report()
print('JSON was received. Sending updated status for process pending...')

def decrypting_data(user_password, secret):
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

try:
    decrypted_pass = decrypting_data(user_password, secret)
except Exception as e:
    requests.post(f'{error_status}{runId}', json={'ErrorMessage' : str(e)})
    print(e)
    browser.click_element('Error with decoding')

def live_logging(current_status):
    global totally_reconciled
    global transaction_counter
    global comment_count
    send_status = {'data': f'{actual_time()} {current_status}'}
    requests.post(f'{status_sender_url}{runId}', json=send_status)

def grabbing_table_values():
    global transaction_counter
    left_company_name_text = browser.get_text(left_company_name)
    right_compamy_name_text = browser.get_text(right_compamy_name)
    if browser.does_page_contain_element(left_ref_field):
        ref_left_text = str(browser.get_text(left_ref_field)).replace(',','.')
    else:
        ref_left_text = '-'
    if browser.does_page_contain_element(left_amount_spent):
        amount_spent_left_text = str(browser.get_text(left_amount_spent)).replace(',','.')
        amount_spent_right_text = str(browser.get_text(right_amount_spent)).replace(',','.')
    else:
        amount_spent_left_text = '-'
        amount_spent_right_text = '-'
    if browser.does_page_contain_element(left_amount_received):
        amount_received_left_text = str(browser.get_text(left_amount_received)).replace(',','.')
        amount_received_right_text = str(browser.get_text(right_amount_received)).replace(',','.')
    else:
        amount_received_left_text = '-'
        amount_received_right_text = '-'
    if browser.does_page_contain_element(right_ref_field):
        ref_right_text = str(browser.get_text(right_ref_field)).replace(',','.')
    else: 
        ref_right_text = '-'

    report_row = str(f'{transaction_counter},{left_company_name_text},{ref_left_text},{amount_spent_left_text},{amount_received_left_text},,{right_compamy_name_text},{ref_right_text},{amount_spent_right_text},{amount_received_right_text}\n')
    report.write(report_row)
    transaction_counter += 1
    live_logging(f'Transaction {transaction_counter} matched for {left_company_name_text}')


def logging_xero(user_name, user_password):
    browser.open_available_browser(url)
    browser.maximize_browser_window()
    browser.input_text('xpath=//*[@id="xl-form-email"]', user_name)
    time.sleep(1)
    browser.input_text('xpath=//*[@id="xl-form-password"]', user_password)
    browser.click_element('xpath=//*[@id="xl-form-submit"]')
    print('Successfully authorized...')
    live_logging('Logging in...')

def otp_auth():
    resp = requests.get(f'{otp_get_url}{runId}').json()
    fin_otp = resp['data']['otp']
    time.sleep(1)
    browser.execute_javascript(f'document.querySelector("[placeholder]").value = \"{fin_otp}\"')
    time.sleep(1)
    browser.click_element('//*[@data-automationid="auth-submitcodebutton"]')
    live_logging('Generating 2-auth pass...')
    time.sleep(3)
    live_logging('Successfully logged in...')


def select_organisation():
    browser.go_to(f'{base_url_link_organization}{shortCode_link}')
    time.sleep(3)
    live_logging(f'Selecting company {organization_name}')

def send_files(result_time, operation_status):
        report.close()
        summary_report.close()
        not_matched_report.close()
        
        payload={'timeSpent': str(result_time)}
        
        files=(
        ('files',('report_matched.csv', open(f'./output/{runId}/report_matched.csv', 'rb'), 'application/octet-stream')),
        ('files',('report_not_matched.csv', open(f'./output/{runId}/report_not_matched.csv', 'rb'), 'application/octet-stream')),
        ('files',('summary_report.txt', open(f'./output/{runId}/summary_report.txt', 'rb'), 'application/octet-stream')),
        )
        response_send_files = requests.post(f'{url_temp_send_files}{runId}/{operation_status}', data=payload, files=files,
                    headers={'secret': 'secret'})
        print(response_send_files)

def check_reconcile_exist():
    global totally_reconciled
    if browser.does_page_contain_element(f'(//*[text()[contains(.,"Reconcile ")]])[{1}]'):
        browser.click_element(f'(//*[text()[contains(.,"Reconcile ")]])[{1}]')
        totally_reconciled = browser.get_text('//*[@data-automationid="reconcileBankItems"][1]')
        time.sleep(1)
        check_next_page_exist()
        output_summary_report()
        live_logging(f'Successfully finished processing {totally_reconciled} bank statement lines')
        time.sleep(1)
        end_time = time.time()
        result_time = end_time - start_time
        print(result_time)

        requests.post(f'{status_sender_url}{runId}', json={ 'data': f'{actual_time()} Calculating invoices... Processed {totally_reconciled} bank statement lines', 'totallyReconciled': int(totally_reconciled), 'companyName': company_name, 'organizationId': organizationId }) 

        print(runId)
        send_files(result_time, 'completed')

        # requests.post(f'{status_sender_url}{runId}', json={ 'data':'End.'} )

    else:
        requests.post(f'{status_sender_url}{runId}', json={'data': f'{actual_time()} There\'s no invoices to reconcile.','totallyReconciled': '0', 'companyName': company_name, 'organizationId': organizationId}) 
        send_files('10', 'completed')

        return
    time.sleep(2)



def ok_press():
    global rule_transactions
    global transaction_counter

    while browser.is_element_visible('(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]/../..//*[@class="info c3"]//label') and browser.get_text('(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]/../..//*[@class="info c3"]//label') == 'Apply rule':
        left_company_name_text = browser.get_text(left_company_name)
        if browser.does_page_contain_element(left_amount_spent):
            amount_spent_left_text = str(browser.get_text(left_amount_spent)).replace(',','.')
        else:
            amount_spent_left_text = '-'
        if browser.does_page_contain_element(left_amount_received):
            amount_received_left_text = str(browser.get_text(left_amount_received)).replace(',','.')
        else:
            amount_received_left_text = '-'

        report_row = str(f'{transaction_counter},{left_company_name_text}, ,{amount_spent_left_text},{amount_received_left_text},"Rule for transaction aplied",,,\n')
        report.write(report_row)
        browser.set_focus_to_element('(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]')
        browser.click_element('(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]')
        time.sleep(3)
        transaction_counter += 1
        live_logging(f'Transaction {transaction_counter} matched with rule for {left_company_name_text}')
        
    browser.reload_page()
    while browser.does_page_contain_element('(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]'):
        if browser.is_element_visible(right_amount_spent) == True or browser.is_element_visible(right_amount_received) == True:
            grabbing_table_values()
        browser.click_element(
            '(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]')
        time.sleep(3)
        line_warn = 0
        print(f'====> Reconciled {transaction_counter} invoice sucessfully... Next invoice processing<====')
        if browser.does_page_contain_element('//*[@class=" x-window"]'):
            browser.click_element(
                '//*[@class=" x-btn-text" and text()[contains(.,"Cancel")]]')
            time.sleep(2)
            browser.reload_page()
            browser.wait_until_page_contains_element('(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]')
            line_warn = browser.get_element_attribute('(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]/../..', 'data-index')
            browser.click_element(f'//*[@id="statementLines"]/div[@data-index="{line_warn}"]//*[@class="t4"]')
            browser.input_text(
                f'//*[@id="statementLines"]/div[@data-index="{line_warn}"]//div[@class="info c5"]/textarea', phrase_if_error_exist, clear=True)
            time.sleep(1)
            browser.press_keys(None, "CTRL+s")
            print('====>Leaving comment for non mathcing invoice. Please check it.<====')
            time.sleep(3)

### Not matched transactions selectors
not_matched_date = '(//*[@data-index]/div[@class="statement create"]/div/a[@class="t4"])[1]/../../..//*[@class="info"]//*[@class="details"]/span[1]'
not_matched_company_name = '(//*[@data-index]/div[@class="statement create"]/div/a[@class="t4"])[1]/../../..//*[@class="info"]//*[@class="details"]/span[2]'
not_matched_spent = '(//*[@data-index]/div[@class="statement create"]/div/a[@class="t4"])[1]/../../..//*[@class="info"]//*[@class="amount spent set"]'
not_mathed_received = '(//*[@data-index]/div[@class="statement create"]/div/a[@class="t4"])[1]/../../..//*[@class="info"]//*[@class="amount received set"]'

def comments_leave():
  while browser.does_page_contain_element('(//*[@data-index]/div[@class="statement create"]/div/a[@class="t4"])[1]'):
    global comment_count
    not_mathced_date_text = browser.get_text(not_matched_date)
    not_mathced_company_name_text = browser.get_text(not_matched_company_name)
    if browser.does_page_contain_element(not_matched_spent):
        not_matched_spent_text = str(browser.get_text(not_matched_spent)).replace(',','.')
    else:
        not_matched_spent_text = '-'
    if browser.does_page_contain_element(not_mathed_received):
        not_mathed_received_text = str(browser.get_text(not_mathed_received)).replace(',','.')
    else:
        not_mathed_received_text = '-'
    
    not_matched_report.write(f'{comment_count},{not_mathced_date_text},{not_mathced_company_name_text},{not_matched_spent_text},{not_mathed_received_text}\n')


    discuss_id = browser.get_element_attribute('(//*[@data-index]/div[@class="statement create"]/div/a[@class="t4"])[1]/../*[@class="t4"]', 'id')
    text_field_input = browser.get_element_attribute(f'//*[@id="{discuss_id}"]/..//..//..', 'data-index')
    browser.set_focus_to_element('(//*[@data-index]/div[@class="statement create"]/div/a[@class="t4"])[1]')
    browser.click_element('(//*[@data-index]/div[@class="statement create"]/div/a[@class="t4"])[1]')
    browser.input_text(f'//*[@data-index="{text_field_input}"]//*[@class="info c5"]/textarea', phrase_for_comment, clear=True)
    time.sleep(1)
    browser.press_keys(None, "CTRL+s")
    print(f'====>Leaving {comment_count}\'s comment for manual invoice checking.<====')
    comment_count += 1
    time.sleep(2)
    live_logging(f'Leaving comment to {comment_count} invoice ==> {not_mathced_company_name_text}')

def check_done():
  if browser.is_element_visible('//*[@id="AllDone"]'):
    print('Processing finished sucessfully.')

def check_next_page_exist():
    while browser.is_element_visible('//*[@id="mainPagerNext" and @style["display:"]]'):
        while browser.does_page_contain_element('(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]'):
            ok_press()
            browser.reload_page()
        comments_leave()
        if browser.is_element_visible('//*[@id="mainPagerNext" and @style["display:"]]'):
            browser.click_element('//*[@id="mainPagerNext" and @style["display:"]]')
        else: return
        time.sleep(2)
        check_done()
        live_logging('Opening next page...')
    else:
        ok_press()
        browser.reload_page()
        comments_leave()
        browser.click_element('//*[@class="xnav-tab"]')

def output_summary_report():
    global totally_reconciled
    live_logging('Report generating...')
    totally_reconciled = re.sub(r'\D', '', totally_reconciled)
    summary_report.write(f'Totally reconcilation robot processed:.........{totally_reconciled} items\n\n')
    summary_report.write(f'Matched invoices detected and processed:.......{transaction_counter - 1}\n\n')
    summary_report.write(f'Comments leave (operator review needed):.......{comment_count}\n\n')
    summary_report.write(f'Transactions that have no aproved rules:.......{rule_transactions}\n\n')



try:
    start_time = time.time()
    logging_xero(user_name, user_password=decrypted_pass)
    otp_auth()
    select_organisation()
    check_reconcile_exist()

except Exception as e:
    requests.post(f'{error_status}{runId}', json={'ErrorMessage': str(e)})
    browser.capture_page_screenshot(f'./output/{runId}/error_place.png')

    send_files(None, 'error')

    print(e)