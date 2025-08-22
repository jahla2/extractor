from fastapi.responses import JSONResponse


class HealthHandler:
    def __init__(self):
        pass
    
    async def handle_health_check(self) -> JSONResponse:
        return JSONResponse(
            content={"ok": True},
            headers={"Content-Type": "application/json"}
        )