from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_bet():
    bet_data = {"event_id": "event_1", "amount": 100.50}

    response = client.post("/bet", json=bet_data)
    assert response.status_code == 200
    response_data = response.json()
    assert "bet_id" in response_data
    bet_id = response_data["bet_id"]

    response = client.get("/bets")
    bets = response.json()
    assert any(bet["bet_id"] == bet_id for bet in bets)


def test_get_bets():
    bet_data = {"event_id": "event_2", "amount": 50.75}
    response = client.post("/bet", json=bet_data)
    bet_id = response.json()["bet_id"]

    response = client.get("/bets")
    assert response.status_code == 200
    bets = response.json()
    assert any(bet["bet_id"] == bet_id for bet in bets)


def test_update_bet_status():
    bet_data = {"event_id": "event_3", "amount": 200.50}
    response = client.post("/bet", json=bet_data)
    bet_id = response.json()["bet_id"]

    update_data = {"event_id": "event_3", "status": "won"}

    response = client.post("/update_bet_status", params=update_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Bet statuses updated"}

    response = client.get("/bets")
    bets = response.json()
    updated_bet = next(bet for bet in bets if bet["bet_id"] == bet_id)
    assert updated_bet["status"] == "won"


def test_update_bet_status_invalid():
    update_data = {
        "event_id": "event_3", "status": "invalid_status"
    }

    response = client.post("/update_bet_status", params=update_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid event status"}


def test_get_event_not_found():
    response = client.get("/events/non_existent_event")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
