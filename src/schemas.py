# src/schemas.py
from pydantic import BaseModel, Field, field_validator

class CalculatorSchema(BaseModel):
    op: str
    val1: int = Field(ge=0, le=1000)
    val2: int = Field(ge=0, le=1000)

    @field_validator("op")
    @classmethod
    def validate_op(cls, value: str) -> str:
        if value not in ("add", "multiply"):
            raise ValueError("INVALID_OPERATION: Only 'add' and 'multiply' allowed.")
        return value


class SecurityLookupSchema(BaseModel):
    cve_id: str = Field(pattern=r"^CVE-\d{4}-\d+$")
    include_mitigation: bool = True
class HashCheckSchema(BaseModel):
    file_Hash: str = Field(min_length=32)
    algorithm: str
    @field_validator("algorithm")
    @classmethod
    def validate_algorithm(cls, value: str) -> str:
        normalized = value.lower()
        if normalized  not in ("md5", "sha256"):
            raise ValueError("INVALID_ALGORITHM: Only 'md5' and 'sha256' allowed.")
        return normalized