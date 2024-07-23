from fastapi import HTTPException, Request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import secrets
from datetime import datetime, timedelta


class ServerSideCSRFSecure:
    def __init__(self, token_lifetime_seconds=900, tokens_lifetime_check_interval=1800):
        self.tokens = {}
        self.token_lifetime = timedelta(seconds=token_lifetime_seconds)

        scheduler = BackgroundScheduler()
        scheduler.add_job(self.clean_up_tokens, IntervalTrigger(seconds=tokens_lifetime_check_interval))
        scheduler.start()

    def generate_token(self, request: Request):
        ip = request.client.host
        if ip in self.tokens and datetime.now() - self.tokens[ip]["token_generate_time"] < self.token_lifetime:
            return self.tokens[ip]["token"]

        token = secrets.token_hex(16)
        self.tokens[ip] = {"token": token, "token_generate_time": datetime.now()}
        return token

    def validate_token(self, request: Request, token: str):
        ip = request.client.host
        now = datetime.now()
        if ip in self.tokens:
            stored_token = self.tokens[ip]["token"]
            token_generate_time = self.tokens[ip]["token_generate_time"]
            if stored_token == token and now - token_generate_time < self.token_lifetime:
                del self.tokens[ip]
                return
            del self.tokens[ip]
        raise HTTPException(detail="Invalid or expired CSRF token", status_code=422)

    def clean_up_tokens(self):
        now = datetime.now()
        expired_ips = []

        for ip, data in self.tokens.items():
            if now - data["token_generate_time"] < self.token_lifetime:
                expired_ips.append(ip)

        for ip in expired_ips:
            del self.tokens[ip]
