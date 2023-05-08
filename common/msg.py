from pydantic.main import BaseModel
from enum import Enum


class Button(BaseModel):
    type = "ok"
    text = "확인"
    link = ""

    def __init__(
        self,
        type: str,
        text: str,
        link: str,
    ):
        super().__init__()
        self.type = type
        self.text = text
        self.link = link

    def to_dict(self):
        result = {
            "type": self.type,
            "text": self.text,
            "link": self.link,
        }

        return result


class LinkPage(str, Enum):
    LOGIN = 'login'
    HOME = 'home'


class BtnType(str, Enum):
    OK = 'ok'
    NORMAL = 'normal'
    DANGER = 'danger'
