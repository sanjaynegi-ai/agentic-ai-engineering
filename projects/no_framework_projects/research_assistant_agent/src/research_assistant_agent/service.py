from pathlib import Path
from pydantic import BaseModel, Field
class ResearchAnswer(BaseModel): answer: str; citations: list[str] = Field(default_factory=list); grounded: bool
DATA=Path(__file__).resolve().parents[2]/"data/notes"
def run(text: str) -> ResearchAnswer:
    query={word.lower().strip(".,?!") for word in text.split() if len(word)>3}
    ranked=[]
    for path in DATA.glob("*.md"):
        content=path.read_text(encoding="utf-8"); score=sum(word in content.lower() for word in query)
        if score: ranked.append((score,path,content))
    ranked.sort(reverse=True,key=lambda item:item[0])
    if not ranked: return ResearchAnswer(answer="I do not have enough evidence in the local notes.",grounded=False)
    return ResearchAnswer(answer=ranked[0][2].splitlines()[-1],citations=[f"{ranked[0][1].name}:1"],grounded=True)
