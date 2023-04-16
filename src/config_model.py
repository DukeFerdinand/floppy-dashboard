from typing import List, Optional
from pydantic import BaseModel

class Pane(BaseModel):
    command: str
    host: Optional[str]


class Window(BaseModel):
    name: str
    panes: List[Pane]


class Host(BaseModel):
    name: str
    host: str
    username: str
    password: Optional[str]
    key: Optional[str]

    def __validate__(self):
        if self.password is None and self.key is None:
            raise ValueError("Either password or key must be set for host '" + self.name + "'")


class Config(BaseModel):
    session_name: str
    windows: List[Window]
    hosts: Optional[List[Host]]
