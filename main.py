import socket

from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Task Management API")

# Allow the frontend (e.g. a Next.js dev server on another origin) to call this
# API directly from the browser. Tighten allow_origins to your frontend's exact
# origin(s) before deploying to production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class Operands(BaseModel):
    a: float
    b: float

class Item(BaseModel):
    name: str
    description: Optional[str] = None


items: Dict[int, Item] = {
    1: Item(name="item1", description="first item"),
    2: Item(name="item2", description="second item"),
    3: Item(name="item3", description="third item"),
}

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/")
def root() -> dict:
    return {"message": "it works !"}


@app.get("/addition")
def addition(a: int, b: int) -> dict:
    return {"result a+b=": a + b, "developer": "Dev1"}


def current_ip() -> str:
    """IP address of the network interface connected to the Internet."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


@app.get("/greeting")
def greeting(name: str) -> dict:
    return {
        "message": f"Hello, {name}",
        "developer": "Dev2",
        "hostname": socket.gethostname(),
        "IP": current_ip(),
    }


@app.post("/multiply")
def multiply(op: Operands) -> dict:
    return {"result a*b=": op.a * op.b, "developer": "Dev1"}


@app.post("/divide")
def divide(op: Operands) -> dict:
    if op.b == 0:
        raise HTTPException(status_code=400, detail="Division by zero")
    return {"result a/b=": op.a / op.b, "developer": "Dev2"}

@app.get("/items")
def list_items() -> List[dict]:
    return [{"id": k, **v.model_dump()} for k, v in items.items()]


@app.delete("/remove/{item_id}")
def remove(item_id: int) -> dict:
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    del items[item_id]
    return {"deleted": item_id, "developer": "Dev1"}