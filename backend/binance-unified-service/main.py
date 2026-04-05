from fastapi import FastAPI
app = FastAPI(title="TigerEx binance-unified-service")
@app.get("/")
async def index(): return {"message": "TigerEx binance-unified-service Operational"}
@app.get("/health")
async def health(): return {"status": "healthy"}
