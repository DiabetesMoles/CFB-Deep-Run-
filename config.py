import os
from dataclasses import dataclass
@dataclass(frozen=True)
class Settings:
    api_key:str=os.getenv("CFBD_API_KEY","")
    base_url:str=os.getenv("CFBD_BASE_URL","https://api.collegefootballdata.com").rstrip("/")
    season:int=int(os.getenv("CFB_SEASON","2026"))
    simulations:int=int(os.getenv("SIMULATIONS","50000"))
    model_path:str=os.getenv("MODEL_PATH","data/cfb_model.joblib")
settings=Settings()
