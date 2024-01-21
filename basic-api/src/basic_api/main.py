import uvicorn

if __name__ == "__main__":
    uvicorn.run("basic_api.main:app", host="0.0.0.0", log_level="info")
