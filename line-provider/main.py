import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from enum import Enum


class EventState(str, Enum):
    not_completed = "not_completed"
    completed_first_team_win = "completed_first_team_win"
    completed_second_team_win = "completed_second_team_win"


class Event(BaseModel):
    event_id: str
    coefficient: float
    deadline: int
    state: EventState


class EventCreate(BaseModel):
    event_id: str
    coefficient: float
    deadline: int


class EventUpdate(BaseModel):
    state: EventState


app = FastAPI()

events = {}


@app.post("/events", response_model=Event)
async def create_event(event: EventCreate):
    if event.event_id in events:
        raise HTTPException(status_code=400, detail="Event with this ID already exists")
    events[event.event_id] = Event(
        event_id=event.event_id,
        coefficient=event.coefficient,
        deadline=int(time.time())+event.deadline,
        state=EventState.not_completed
    )
    return events[event.event_id]


@app.get("/events", response_model=List[Event])
async def list_events():
    return list(events.values())


@app.get("/events/{event_id}", response_model=Event)
async def get_event(event_id: str):
    event = events.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.put("/events/{event_id}/status", response_model=Event)
async def update_event_status(event_id: str, event_update: EventUpdate):
    event = events.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    event.state = event_update.state
    return event
