import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test."""
    from src.app import activities
    
    original_state = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Competitive soccer team practicing skills and playing matches",
            "schedule": "Mondays, Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Pickup games, drills, and intramural tournaments",
            "schedule": "Tuesdays and Thursdays, 5:00 PM - 7:00 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["mia@mergington.edu", "charlotte@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting workshops, rehearsals, and school productions",
            "schedule": "Fridays, 4:00 PM - 6:30 PM",
            "max_participants": 30,
            "participants": ["henry@mergington.edu", "amelia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Prepare for interschool debates and practice public speaking",
            "schedule": "Mondays, 3:45 PM - 5:15 PM",
            "max_participants": 16,
            "participants": ["logan@mergington.edu", "grace@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Build and program robots for competitions and learning",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["jack@mergington.edu", "eva@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_state)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_state)
