import json
import os
os.environ["DATABASE_URL"] = "sqlite:///./test_pocketsmart.db"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["GEMINI_API_KEY"] = ""

from app.config import get_settings
get_settings.cache_clear()

from app.models.database import init_db
init_db()

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def auth():
    r = client.post('/register', json={'name':'Test User','email':'test@example.com','password':'password123'})
    if r.status_code == 409:
        r = client.post('/login', json={'email':'test@example.com','password':'password123'})
    return {'Authorization':'Bearer '+r.json()['access_token']}

def test_startup():
    r = client.get('/startup')
    assert r.status_code == 200
    assert r.json()['status'] == 'ready'

def test_guest_session():
    r = client.get('/session-info')
    assert r.status_code == 200
    assert r.json()['logged_in'] is False

    r2 = client.get('/session-data')
    assert r2.status_code == 200
    assert r2.json()['logged_in'] is False

def test_authenticated_me():
    h = auth()
    r = client.get('/me', headers=h)
    assert r.status_code == 200
    assert r.json()['email'] == 'test@example.com'

def test_register_and_home():
    h = auth()
    r = client.post('/generate-home', headers=h, json={
        'budget': 50000,
        'room_type': 'Living Room',
        'style': 'Modern',
        'items': [{'category': 'Lighting', 'quantity': 2}],
        'location': 'India',
        'notes': ''
    })
    assert r.status_code == 200
    assert r.json()['planner'] == 'home'
    assert r.json()['source'] == 'fallback'
    assert 'history_id' in r.json()

def test_party():
    h = auth()
    r = client.post('/generate-party', headers=h, json={
        'budget': 30000,
        'guests': 30,
        'event_type': 'Birthday',
        'venue': 'Hall',
        'city': 'Coimbatore',
        'food_preference': 'Mixed',
        'notes': ''
    })
    assert r.status_code == 200
    assert len(r.json()['recommendations']) >= 1

def test_jewelry_and_history():
    h = auth()
    payload = {
        'budget': 15000,
        'occasion': 'Wedding',
        'style': 'Elegant',
        'outfit_color': 'Royal Blue',
        'jewelry_type': 'Necklace',
        'notes': 'Gold accent preferred'
    }
    r = client.post('/generate-jewelry', headers=h, data={'payload': json.dumps(payload)})
    assert r.status_code == 200
    data = r.json()
    assert data['planner'] == 'jewelry'
    history_id = data['history_id']

    hr = client.get('/history', headers=h)
    assert hr.status_code == 200
    assert len(hr.json()) >= 1

    dr = client.get(f'/recommendations-details/{history_id}', headers=h)
    assert dr.status_code == 200
    assert dr.json()['id'] == history_id


