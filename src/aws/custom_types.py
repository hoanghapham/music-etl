from pydantic import BaseModel

class Column(BaseModel):
    column_name: str
    data_type: str

class Table(BaseModel):
    table_name: str
    schema_name: str
    columns: list[Column]
