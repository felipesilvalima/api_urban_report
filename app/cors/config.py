from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def corsConfig(app: FastAPI):
    # Defina a lista de origens primeiro
    origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://lovable.dev",  
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins, 
        allow_origin_regex=r"https://id-preview--.*\.lovable\.app",
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Accept",
            "Origin",
            "X-Requested-With",
            "ngrok-skip-browser-warning",
        ],
        expose_headers=["Authorization"],
        max_age=600,
    )
    