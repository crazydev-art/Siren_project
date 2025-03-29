from fastapi import FastAPI
from app.routes import nafv2,auth,siren,siret,compagny
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Siren API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all frontend  domains (update for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods, including OPTIONS
    allow_headers=["*"],  # Allow all headers
)


app.include_router(nafv2.router, prefix="", tags=["NAF V2"])
app.include_router(auth.router, prefix="/auth", tags=["Admin Auth"])
app.include_router(siren.router, prefix="/api", tags=["SIREN Search"])
app.include_router(siret.router, prefix="/api", tags=["SIRET Search"])
app.include_router(compagny.router, prefix="/api", tags=["SIRET Search"])

