from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
from .weather_client import get_weather_by_city

app = FastAPI(title="Weather Proxy API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/weather")
async def weather(city: str = Query(..., description="Nama kota, contoh: Jakarta"),
                  lang: Optional[str] = Query("en", description="Kode bahasa untuk hasil geocoding")):
    try:
        data = await get_weather_by_city(city.strip(), lang)
        if data is None:
            raise HTTPException(status_code=404, detail=f"Kota '{city}' nggak ketemu")
        return JSONResponse(data)
    except HTTPException:
        raise
    except Exception as e:
        # Log seharusnya di sini (print/Logger)
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}")