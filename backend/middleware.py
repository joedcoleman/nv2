import toml
from fastapi import Request, HTTPException

config = toml.load("../settings.toml")


async def auth_middleware(request: Request, call_next):
    if "/auth" not in request.url.path:
        authorization = request.headers.get("Authorization")
        if authorization != f"Bearer {config['auth']['token']}":
            raise HTTPException(status_code=401, detail="Unauthorized")
    response = await call_next(request)
    return response
