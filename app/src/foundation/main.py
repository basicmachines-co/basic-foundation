import uvicorn


def run():
    uvicorn.run("foundation.app:app", host="0.0.0.0", log_level="info", reload=True)


if __name__ == "__main__":
    run()
