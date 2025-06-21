from pydantic import BaseModel, conint
from typing import Dict

class SurahMappingSchema(BaseModel):
    surah_mapping: Dict[str, conint(ge=1, le=114)]