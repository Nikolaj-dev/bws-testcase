import time
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_create_event():
    event_data = {
        "event_id": "event_1",
        "coefficient": 1.5,
        "deadline": 3600
    }

    response = client.post("/events", json=event_data)
    assert response.status_code == 200
    event = response.json()
    assert event["event_id"] == event_data["event_id"]
    assert event["coefficient"] == event_data["coefficient"]
    assert event["state"] == "not_completed"
    assert event["deadline"] > int(time.time())


def test_list_events():
    response = client.get("/events")
    assert response.status_code == 200
    events = response.json()
    assert isinstance(events, list)


def test_get_event():
    event_data = {
        "event_id": "event_2",
        "coefficient": 2.0,
        "deadline": 1800
    }
    client.post("/events", json=event_data)  # Создаем событие

    response = client.get(f"/events/{event_data['event_id']}")
    assert response.status_code == 200
    event = response.json()
    assert event["event_id"] == event_data["event_id"]
    assert event["coefficient"] == event_data["coefficient"]


def test_update_event_status():
    event_data = {
        "event_id": "event_3",
        "coefficient": 3.0,
        "deadline": 7200  # 2 часа
    }
    client.post("/events", json=event_data)  # Создаем событие

    update_data = {
        "state": "completed_first_team_win"
    }

    response = client.put(f"/events/{event_data['event_id']}/status", json=update_data)
    assert response.status_code == 200
    updated_event = response.json()
    assert updated_event["state"] == update_data["state"]


def test_get_event_not_found():
    response = client.get("/events/non_existent_event")
    assert response.status_code == 404
    assert response.json() == {"detail": "Event not found"}


def test_create_event_duplicate():
    event_data = {
        "event_id": "event_4",
        "coefficient": 1.75,
        "deadline": 3600
    }
    client.post("/events", json=event_data)
    response = client.post("/events", json=event_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Event with this ID already exists"}
