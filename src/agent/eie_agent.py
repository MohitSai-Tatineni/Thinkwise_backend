from pydantic import BaseModel
from langchain_ollama import ChatOllama
from typing import Optional, List, Dict


class Assistant(BaseModel):
    idea : Dict
    EIE_score : List[int]
    top_3_eie : Dict



## Tools



## Nodes

# Node - 1 :
def eie_assistant(input : Dict) -> Dict :
    return


## Graph Build