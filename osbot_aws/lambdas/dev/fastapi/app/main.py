from fastapi import FastAPI
from mangum  import Mangum

from osbot_aws.lambdas.dev.fastapi.app.api.api import router

app = FastAPI(root_path="/prod")


@app.get("/")
async def root():
    return {"message": "Hello from FastApi"}


app.include_router(router, prefix="/api/v1")
handler = Mangum(app)