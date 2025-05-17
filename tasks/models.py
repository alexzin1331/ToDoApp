from selectors import BaseSelector

from pydantic import BaseModel

class TaskModel(BaseModel):
    id: int
    name: str
    description: str | None = None

class AddRequest(BaseModel):
    name: str
    description: str | None = None


class TaskID(BaseModel):
    id: int

class EditRequest(BaseModel):
    id: int
    name: str | None = None
    description: str | None = None

