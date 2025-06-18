from pydantic import BaseModel, Field
from typing import List, Dict
import yaml
from pathlib import Path


class GradingItem(BaseModel):
    score: int
    keywords: List[str]


class GradingCategory(BaseModel):
    __root__: Dict[str, GradingItem]


class GradingKeywords(BaseModel):
    authenticity: GradingCategory
    isnaad_status: GradingCategory


def load_grading_config(path: str = 'config/grading_keywords.yaml') -> GradingKeywords:
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return GradingKeywords(**data)
