import os
from dotenv import load_dotenv


load_dotenv()

class Settings:
    # ---- CONFIG GOOGLE EARTH ENGINE ----
    PROJECT_NAME = os.getenv("GOOGLE_EARTH_ENGINE_PROJECT_NAME")
    SHAPEFILE = os.getenv("GOOGLE_EARTH_ENGINE_SHAPEFILE")

    SCALE_CHIRPS = 5000
    SCALE_ERA5 = 9000

    # ---- GENERAL CONFIG ----
    START_YEAR = 2022
    END_YEAR = 2024

    # --- CONFIG BPS -----
    API_KEY = os.getenv("BPS_API_KEY")
    
conf = Settings()