from pydantic import BaseModel
from typing import List

class ArabicNERConfigSchema(BaseModel):
    before_honorifics: List[str]
    after_honorifics: List[str]
    prophet_titles: List[str]
    prophet_honorifics: List[str]
    companion_honorifics: List[str]
    scholar_honorifics: List[str]
    allah_references: List[str]
    cities: List[str]
    common_names: List[str]
    special_titles: List[str]
    

class ArabicNERSchema(BaseModel):
    """Schema for Arabic Named Entity Recognition (NER) configuration."""
    
    ner_config: ArabicNERConfigSchema
    
    class Config:
        """Pydantic configuration."""
        title = "Arabic NER Configuration"
        description = "Configuration schema for Arabic Named Entity Recognition."
        extra = "forbid"  # Disallow extra fields not defined in the schema
        allow_population_by_field_name = True  # Allow population by field names
        
    @classmethod
    def from_dict(cls, data: dict):
        """Create an instance from a dictionary."""
        return cls(**data)  
    def to_dict(self) -> dict:
        """Convert the instance to a dictionary."""
        return self.dict(by_alias=True, exclude_unset=True)
    def validate(self):
        """Validate the configuration schema."""
        self.ner_config.validate()
        return True
    def __str__(self):
        """String representation of the schema."""
        return f"Arabic NER Schema: {self.ner_config.json(indent=2)}"
        