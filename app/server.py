from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


app = FastAPI()


# TODO: Change origin to real domain to reject Ajax requests from elsewhere
app.add_middleware(CORSMiddleware, allow_origins=['*'])


@app.get('/generate/{midi}')
def generate_music(midi: str):
    return {"data": midi}

