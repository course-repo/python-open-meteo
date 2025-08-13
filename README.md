# Weather Proxy API (FastAPI + Open‑Meteo)

## Jalankan secara lokal

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Buka:
- http://localhost:8000/health
- http://localhost:8000/weather?city=Jakarta

## Kenapa begini?
- **Tanpa API key**: pakai Open‑Meteo & geocoding mereka.
- **Cache 5 menit**: hemat call & lebih cepat.
- **Payload simpel**: lokasi, cuaca saat ini, dan 24 jam ke depan.

## Extend cepat
- Tambah param `hours=48` → ubah slicing `[:24]` jadi dinamis.
- Tambah unit (Fahrenheit) → terima `unit=temp_f` dan konversi.
- Tambah endpoint `/forecast/daily` → gunakan parameter `daily=` dari Open‑Meteo.

## Deployment
- Gunakan Docker / Railway / Fly.io. Contoh perintah Docker sederhana:

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t weather-proxy .
docker run -p 8000:8000 weather-proxy
```