from os.path import join, dirname
from RPA.Browser.Selenium import Selenium
import os
import time
import json
import requests
import sys
import re
from dotenv import load_dotenv
import utils

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

browser = Selenium()

received = sys.argv[1]
received = json.loads(received)

error_status = os.environ['ERRORS_SEND_URL']
status_sender_url = os.environ['URL_FOR_LOGS']
otp_get_url = os.environ['OTP_GET_URL']
url_temp_send_files = os.environ['URL_FOR_UPLOAD']

# Variables
url_Xero = 'https://login.xero.com/identity/user/login'
user_name = received['userName']
user_password = received['userPassword'] 
organization_name =  received['organizationName']
phrase_for_comment = received['commentPhrase']
phrase_if_error_exist = received['errorPhrase']
phrase_for_cheking_rule = 'The rule on this transaction need additional check by operator.'
bank_quantity = received['bankQuantity']
base_url_link_organization = 'https://go.xero.com/OrganisationLogin/?shortCode='
shortCode_link = received['shortCode']
company_name = received['companyName']
organizationId = received['organizationId']
runId = received['runId']
secret = os.environ['SECRET']
comment_status = received['is_comment_enabled']

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
transaction_counter = 0
comment_count = 1
rule_transactions = 0
totally_reconciled = ''
statusReconcile = ''

os.makedirs(f'./output/{runId}', exist_ok=True)

matched_report = utils.Reports.create_matched_report(runId, organization_name)
not_matched_report = utils.Reports.create_not_matched_report(runId, organization_name)
summary_report = utils.Reports.create_summary_report(runId, organization_name)

utils.StatusLog.send_start_processing_log(runId)

try:
    decrypted_pass = utils.decrypt_user_password(user_password, secret)
except Exception as e:
    utils.StatusLog.send_error_message(runId, e)
    print(e)

def live_logging(current_status):
    global totally_reconciled
    global transaction_counter
    global comment_count
    utils.StatusLog.send_live_log(runId, current_status)

def grabbing_table_values():
    global transaction_counter
    if browser.get_element_attribute(left_company_name, 'title'):
        left_company_name_text = browser.get_element_attribute(left_company_name, 'title')
    else:
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
    matched_report.write(report_row)
    transaction_counter += 1
    live_logging(f'Transaction №{transaction_counter} matched for {left_company_name_text}')


def logging_xero(user_name, user_password):
    browser.open_available_browser(url_Xero)
    browser.maximize_browser_window()
    browser.input_text('xpath=//*[@id="xl-form-email"]', user_name)
    time.sleep(1)
    browser.input_text('xpath=//*[@id="xl-form-password"]', user_password)
    browser.click_element('xpath=//*[@id="xl-form-submit"]')
    print('Successfully authorized...')
    live_logging('Logging in...')

def otp_auth():
    otp = utils.get_otp(runId)
    time.sleep(1)
    browser.execute_javascript(f'document.querySelector("[placeholder]").value = \"{otp}\"')
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
        matched_report.close()
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
        message_json = {'data': f'{utils.Time.actual_time()} Calculating invoices... Processed {totally_reconciled} bank statement lines', 'totallyReconciled': int(totally_reconciled), 'companyName': company_name, 'organizationId': organizationId }

        utils.StatusLog.send_final_log(runId, message_json)

        send_files(result_time, 'completed')

        message_end_json = { 'data':'End.' }
        utils.StatusLog.send_final_log(runId, message_end_json)

    else:
        message_no_reconcile_json = {'data': f'{utils.Time.actual_time()} There\'s no invoices to reconcile.','totallyReconciled': '0', 'companyName': company_name, 'organizationId': organizationId}
        utils.StatusLog.send_final_log(runId, message_no_reconcile_json)
        send_files('10', 'completed')

        return
    time.sleep(2)

def rule_aprove():
    global transaction_counter

    while browser.does_page_contain_element('((//*[@class="statement create ruled"])//..//*[@class="xbtn skip okayButton exclude" and @style="visibility: visible;"])[1]'):   
        #### Long name test
        if browser.get_element_attribute(left_company_name, 'title'):
            left_company_name_text = browser.get_element_attribute(left_company_name, 'title')
        else:
            left_company_name_text = browser.get_text(left_company_name)
        ####
        if browser.does_page_contain_element(left_amount_spent):
            amount_spent_left_text = str(browser.get_text(left_amount_spent)).replace(',','.')
        else:
            amount_spent_left_text = '-'
        if browser.does_page_contain_element(left_amount_received):
            amount_received_left_text = str(browser.get_text(left_amount_received)).replace(',','.')
        else:
            amount_received_left_text = '-'

        report_row = str(f'{transaction_counter},{left_company_name_text}, ,{amount_spent_left_text},{amount_received_left_text},"Rule for transaction aplied",,,\n')
        matched_report.write(report_row)
        browser.set_focus_to_element('((//*[@class="statement create ruled"])//..//*[@class="xbtn skip okayButton exclude" and @style="visibility: visible;"])[1]')
        browser.click_element('((//*[@class="statement create ruled"])//..//*[@class="xbtn skip okayButton exclude" and @style="visibility: visible;"])[1]')
        time.sleep(3)
        transaction_counter += 1

        live_logging(f'Transaction №{transaction_counter} matched with rule for {left_company_name_text}')

def ok_press():
    global rule_transactions
    global transaction_counter

    #while browser.is_element_visible('(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]/../..//*[@class="info c3"]//label') and browser.get_text('(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]/../..//*[@class="info c3"]//label') == 'Apply rule':
    #while browser.is_element_visible('((//label[text()="Apply rule"])/../../../..//*[@class="xbtn skip okayButton exclude" and @style="visibility: visible;"])[1]'):
    rule_aprove()
        
    browser.reload_page()
    while browser.does_page_contain_element('(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]'):
        if browser.is_element_visible(right_amount_spent) == True or browser.is_element_visible(right_amount_received) == True:
            grabbing_table_values()
        browser.click_element(
            '(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]')
        time.sleep(3)
        line_warn = 0
        
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

        if browser.does_page_contain_element('((//*[@class="statement create ruled"])//..//*[@class="xbtn skip okayButton exclude" and @style="visibility: visible;"])[1]'):
            rule_aprove()



### Not matched transactions selectors
not_matched_date = '(//*[@data-index]/div[@class="statement create"]/div/a[@class="t4"])[1]/../../..//*[@class="info"]//*[@class="details"]/span[1]'
not_matched_company_name = '(//*[@data-index]/div[@class="statement create"]/div/a[@class="t4"])[1]/../../..//*[@class="info"]//*[@class="details"]/span[2]'
not_matched_spent = '(//*[@data-index]/div[@class="statement create"]/div/a[@class="t4"])[1]/../../..//*[@class="info"]//*[@class="amount spent set"]'
not_mathed_received = '(//*[@data-index]/div[@class="statement create"]/div/a[@class="t4"])[1]/../../..//*[@class="info"]//*[@class="amount received set"]'

def comments_leave():
  while browser.does_page_contain_element('(//*[@data-index]/div[@class="statement create"]/div/a[@class="t4"])[1]'):
    global comment_count
    not_mathced_date_text = browser.get_text(not_matched_date)

### Long company names processing
    if browser.get_element_attribute(not_matched_company_name, 'title'):
        not_matched_company_name_text = browser.get_element_attribute(not_matched_company_name, 'title')
    else:
        not_matched_company_name_text = browser.get_text(not_matched_company_name)
###
    if browser.does_page_contain_element(not_matched_spent):
        not_matched_spent_text = str(browser.get_text(not_matched_spent)).replace(',','.')
    else:
        not_matched_spent_text = '-'
    if browser.does_page_contain_element(not_mathed_received):
        not_mathed_received_text = str(browser.get_text(not_mathed_received)).replace(',','.')
    else:
        not_mathed_received_text = '-'
    
    not_matched_report.write(f'{comment_count},{not_mathced_date_text},{not_matched_company_name_text},{not_matched_spent_text},{not_mathed_received_text}\n')


    discuss_id = browser.get_element_attribute('(//*[@data-index]/div[@class="statement create"]/div/a[@class="t4"])[1]/../*[@class="t4"]', 'id')
    text_field_input = browser.get_element_attribute(f'//*[@id="{discuss_id}"]/..//..//..', 'data-index')
    browser.set_focus_to_element('(//*[@data-index]/div[@class="statement create"]/div/a[@class="t4"])[1]')
    browser.click_element('(//*[@data-index]/div[@class="statement create"]/div/a[@class="t4"])[1]')
    browser.input_text(f'//*[@data-index="{text_field_input}"]//*[@class="info c5"]/textarea', phrase_for_comment, clear=True)
    time.sleep(1)
    browser.press_keys(None, "CTRL+s")
    comment_count += 1
    time.sleep(2)
    live_logging(f'Leaving comment to {comment_count} invoice ==> {not_matched_company_name_text}')

def check_done():
  if browser.is_element_visible('//*[@id="AllDone"]'):
    print('Processing finished sucessfully.')

def check_next_page_exist():
    while browser.is_element_visible('//*[@id="mainPagerNext" and @style["display:"]]'):
        while browser.does_page_contain_element('(//*[text()[contains(.,"OK")] and @style="visibility: visible;"])[1]'):
            ok_press()
            browser.reload_page()
        if comment_status == True:
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
        if comment_status == True:
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
    utils.StatusLog.send_error_message(runId, e)
    browser.capture_page_screenshot(f'./output/{runId}/error_place.png')

    send_files(None, 'error')

    print(e)