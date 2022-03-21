from .english import LangEng
from .german import LangGer

from enum import Enum

class Language(Enum):

    english =  LangEng
    german =  LangGer

