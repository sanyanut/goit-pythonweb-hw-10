import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from src.api import utils, contacts, auth, users
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from src.conf.limiter import limiter

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=3000, reload=True)