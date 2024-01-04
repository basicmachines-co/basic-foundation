from fastapi import FastAPI

import uvicorn

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run("basic_api.main:app", host="0.0.0.0", log_level="info")
