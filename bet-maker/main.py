import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from uuid import uuid4
import redis
import decimal
import aiohttp
from enum import Enum
import json

r = redis.Redis(host="redis", port=6379, db=0)


class BetStatus(str, Enum):
    pending = "pending"
    won = "won"
    lost = "lost"


class Bet(BaseModel):
    event_id: str
    amount: decimal.Decimal


class BetHistory(BaseModel):
    bet_id: str
    event_id: str
    amount: decimal.Decimal
    status: BetStatus


class BetCreate(BaseModel):
    event_id: str
    amount: decimal.Decimal


app = FastAPI()


async def get_events_from_line_provider():
    url = "http://line-provider:8000/events"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            return []


@app.get("/events")
async def get_events():
    events = await get_events_from_line_provider()
    current_time = int(time.time())
    valid_events = [
        event for event in events
        if event["state"] == "not_completed" and event["deadline"] > current_time
    ]
    return valid_events


@app.post("/bet")
async def place_bet(bet: BetCreate):
    bet_id = str(uuid4())
    bet_data = {
        "event_id": bet.event_id,
        "amount": str(bet.amount),
        "status": BetStatus.pending.value
    }

    try:
        r.set(bet_id, json.dumps(bet_data))  # Сохраняем корректный JSON
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving bet data to Redis: {e}")

    return {"bet_id": bet_id}


@app.get("/bets", response_model=List[BetHistory])
async def get_bets():
    bets = []
    for bet_id in r.keys():
        bet_data = r.get(bet_id).decode("utf-8")  # Декодируем данные из Redis в строку

        try:
            bet_data = json.loads(bet_data)
            bets.append(
                BetHistory(bet_id=bet_id.decode("utf-8"),
                           event_id=bet_data["event_id"],
                           amount=decimal.Decimal(bet_data["amount"]),
                           status=BetStatus(bet_data["status"]))
            )
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail="Error decoding bet data from Redis")
    return bets


@app.post("/update_bet_status")
async def update_bet_status(event_id: str, status: str):
    if status not in [BetStatus.won.value, BetStatus.lost.value]:
        raise HTTPException(status_code=400, detail="Invalid event status")

    for bet_id in r.keys():
        bet_data = r.get(bet_id).decode("utf-8")
        try:
            bet_data = json.loads(bet_data)
            if bet_data["event_id"] == event_id and bet_data["status"] == BetStatus.pending.value:
                bet_data["status"] = status
                r.set(bet_id, json.dumps(bet_data))
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail="Error decoding bet data from Redis")

    return {"message": "Bet statuses updated"}
