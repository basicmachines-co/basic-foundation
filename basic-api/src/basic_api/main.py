import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/public", StaticFiles(directory="public"), name="public")

templates = Jinja2Templates(directory="templates")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse(
        request=request, name="item.html", context={"id": id}
    )


if __name__ == "__main__":
    uvicorn.run("basic_api.main:app", host="0.0.0.0", log_level="info")
