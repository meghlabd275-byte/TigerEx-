from fastapi import FastAPI
app = FastAPI(title="Admin Control")
@app.get("/")
async def root():
    return {"service": "Exchange Admin Control", "status": "operational"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
