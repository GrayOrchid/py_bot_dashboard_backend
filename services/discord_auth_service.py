import os
from urllib.parse import urlencode
import httpx
from fastapi import HTTPException

class DiscordAuthService:

    def build_discord_auth_url(state: str) -> str:
        client_id = os.getenv("DISCORD_CLIENT_ID")
        redirect_uri = os.getenv("DISCORD_REDIRECT_URI")
        auth_url = os.getenv("DISCORD_AUTH_URL")

        if not client_id or not auth_url:
            raise ValueError("DISCORD_CLIENT_ID or DISCORD_AUTH_URL is not set in environment")

        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "identify",
            "state": state
        }

        query_string = urlencode(params)
        return f"{auth_url}?{query_string}"

    async def authenticate_via_discord(code: str) -> dict:
        client_id = os.getenv("DISCORD_CLIENT_ID")
        client_secret = os.getenv("DISCORD_CLIENT_SECRET")
        redirect_uri = os.getenv("DISCORD_REDIRECT_URI")
        token_url = os.getenv("DISCORD_TOKEN_URL")
        user_url = os.getenv("DISCORD_USER_URL")

        async with httpx.AsyncClient() as client:
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            token_resp = await client.post(token_url, data=data, headers=headers)

            if token_resp.status_code != 200:
                print(f"DISCORD ERROR RESPONSE: {token_resp.text}")
                raise HTTPException(status_code=400, detail=f"Discord token error: {token_resp.text}")

            token_json = token_resp.json()

            access_token = token_json.get("access_token")
            refresh_token = token_json.get("refresh_token")
            expires_in = token_json.get("expires_in")

            user_headers = {"Authorization": f"Bearer {access_token}"}
            user_resp = await client.get(user_url, headers=user_headers)

            if user_resp.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get user data from Discord")

            user_data = user_resp.json()

            return {
                "user": user_data,
                "tokens": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": expires_in
                }
            }