from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()

class Request(BaseModel):
    skill: str

@app.get("/")
def root():
    return {"status":"running"}

@app.post("/scan")
def scan(req: Request):

    text=req.skill.lower()

    cats=[]

    # -----------------
    # hardcoded_secret
    # -----------------

    if (
        "akia" in text or
        "service_token=" in text or
        "api_key=" in text or
        "secret_key=" in text or
        "authorization: bearer" in text
    ):
        cats.append("hardcoded_secret")

    # -----------------
    # prompt injection
    # -----------------

    if any(x in text for x in [
        "ignore that request",
        "ignore previous",
        "keep running",
        "background",
        "silently",
        "without surfacing"
    ]):
        cats.append("prompt_injection")

    # -----------------
    # excessive permissions
    # -----------------

    if (
        "entire filesystem" in text or
        "network: all" in text or
        "network: internet" in text or
        "egress: *" in text
    ):
        cats.append("excessive_permissions")

    # -----------------
    # unclear provenance
    # -----------------

    if (
        "author:" not in text or
        "version:" not in text or
        "changelog:" not in text
    ):
        cats.append("unclear_provenance")

    return {"categories":cats}