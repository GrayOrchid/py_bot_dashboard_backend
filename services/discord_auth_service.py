from urllib.parse import urlencode
import httpx
from fastapi import HTTPException
from core import settings


class DiscordAuthService:
    @staticmethod
    def build_discord_link_url(state: str) -> str:

        if not settings.DISCORD_CLIENT_ID or not settings.DISCORD_AUTH_URL:
            raise ValueError("DISCORD_CLIENT_ID or DISCORD_AUTH_URL is not set")

        params = {
            "client_id": settings.DISCORD_CLIENT_ID,
            "redirect_uri": settings.DISCORD_REDIRECT_URI,
            "response_type": "code",
            "scope": "identify",
            "state": state,
        }

        return f"{settings.DISCORD_AUTH_URL}?{urlencode(params)}"

    @staticmethod
    async def authenticate_via_discord(code: str) -> dict:

        async with httpx.AsyncClient() as client:
            data = {
                "client_id": settings.DISCORD_CLIENT_ID,
                "client_secret": settings.DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.DISCORD_REDIRECT_URI,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            token_resp = await client.post(settings.DISCORD_TOKEN_URL, data=data, headers=headers)
            if token_resp.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Discord token error: {token_resp.text}"
                )

            token_json = token_resp.json()
            access_token = token_json.get("access_token")
            refresh_token = token_json.get("refresh_token")
            expires_in = token_json.get("expires_in")

            user_headers = {"Authorization": f"Bearer {access_token}"}
            user_resp = await client.get(settings.DISCORD_USER_URL, headers=user_headers)

            if user_resp.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to get user data from Discord"
                )

            user_data = user_resp.json()

            return {
                "user": user_data,
                "tokens": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": expires_in,
                },
            }