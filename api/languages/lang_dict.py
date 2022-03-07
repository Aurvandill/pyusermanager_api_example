
from abc import abstractclassmethod


class LangDict(dict):
    
    def __getattr__(self,attr):
        return f"{attr} - not translated yet"