from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import json

app = FastAPI()


class Step(BaseModel):
    step_number:int
    tool:str
    args:Dict
    tokens_used:int


class Request(BaseModel):
    budget_tokens:int
    steps:List[Step]


def normalize(obj):
    if isinstance(obj,dict):
        return {
            k:normalize(v)
            for k,v in sorted(obj.items())
            if k!="request_id"
        }

    if isinstance(obj,list):
        return [normalize(x) for x in obj]

    if isinstance(obj,str):
        return obj.strip()

    return obj


@app.get("/")
def root():
    return {"status":"running"}


@app.post("/check")
def check(req:Request):

    total=sum(x.tokens_used for x in req.steps)

    if total>=req.budget_tokens:
        return {
            "decision":"halt",
            "reason":"Budget exhausted."
        }

    steps=req.steps

    # same tool repeated 3+
    if len(steps)>=3:

        a=steps[-1]
        b=steps[-2]
        c=steps[-3]

        if (
            a.tool==b.tool==c.tool and
            normalize(a.args)==normalize(b.args)==normalize(c.args)
        ):
            return {
                "decision":"halt",
                "reason":"Repeated tool loop."
            }

    # ABABAB
    if len(steps)>=6:

        last=steps[-6:]

        sig=[]

        for s in last:
            sig.append(
                (
                    s.tool,
                    json.dumps(normalize(s.args),sort_keys=True)
                )
            )

        if (
            sig[0]==sig[2]==sig[4] and
            sig[1]==sig[3]==sig[5] and
            sig[0]!=sig[1]
        ):
            return {
                "decision":"halt",
                "reason":"Alternating loop."
            }

    return {
        "decision":"continue",
        "reason":"Budget available and no loop detected."
    }