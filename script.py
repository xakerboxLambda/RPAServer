import requests
import time

url_temp_send_files = 'https://f6b3-159-224-233-85.ngrok.io/bots/download/'
runId = 178
payload = {'timeSpent': str(23)}

files=(
('files',('report_matched.csv', open(f'./output/{runId}/report_matched.csv', 'rb'), 'application/octet-stream')),
('files',('report_not_matched.csv', open(f'./output/{runId}/report_not_matched.csv', 'rb'), 'application/octet-stream')),
('files',('summary_report.txt', open(f'./output/{runId}/summary_report.txt', 'rb'), 'application/octet-stream')),
)
response_send_files = requests.post(f'{url_temp_send_files}{runId}/completed', data=payload, files=files, headers={'secret': 'secret'}, json={'timeSpent': str(23)})
time.sleep(1)
# requests.post(f'{url_temp_send_files}{runId}/completed', headers={'secret': 'secret'}, json={'timeSpent': str(23)})
print(response_send_files)