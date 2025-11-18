"""
Tests for the FastAPI activities application.

Covers GET /activities, POST /activities/{activity_name}/signup,
and DELETE /activities/{activity_name}/participants endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_root_redirect(client):
    """Test that / redirects to /static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
    
    def test_get_activities_structure(self, client, reset_activities):
        """Test that each activity has the required structure."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, details in activities.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)
    
    def test_get_activities_chess_club_has_initial_participants(self, client, reset_activities):
        """Test that Chess Club has its initial participants."""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert chess_club["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]
        assert len(chess_club["participants"]) == 2


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_participant_success(self, client, reset_activities):
        """Test successfully signing up a new participant."""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "Signed up" in result["message"]
        assert "newstudent@mergington.edu" in result["message"]
    
    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup actually adds participant to activity."""
        # Signup
        client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
        
        # Verify
        response = client.get("/activities")
        activities = response.json()
        participants = activities["Chess Club"]["participants"]
        
        assert "newstudent@mergington.edu" in participants
        assert len(participants) == 3  # 2 original + 1 new
    
    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        """Test that signing up duplicate participant returns 400."""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        
        result = response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signup to nonexistent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"]
    
    def test_signup_multiple_participants_different_activities(self, client, reset_activities):
        """Test signing up same participant to different activities."""
        email = "testuser@mergington.edu"
        
        # Signup to two activities
        response1 = client.post(f"/activities/Chess%20Club/signup?email={email}")
        response2 = client.post(f"/activities/Programming%20Class/signup?email={email}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both activities have the participant
        response = client.get("/activities")
        activities = response.json()
        
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""
    
    def test_unregister_existing_participant_success(self, client, reset_activities):
        """Test successfully unregistering an existing participant."""
        response = client.delete(
            "/activities/Chess%20Club/participants?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "Unregistered" in result["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes participant from activity."""
        # Unregister
        client.delete("/activities/Chess%20Club/participants?email=michael@mergington.edu")
        
        # Verify
        response = client.get("/activities")
        activities = response.json()
        participants = activities["Chess Club"]["participants"]
        
        assert "michael@mergington.edu" not in participants
        assert len(participants) == 1  # Only daniel left
        assert "daniel@mergington.edu" in participants
    
    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregister from nonexistent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent%20Club/participants?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"]
    
    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Test that unregistering non-participant returns 404."""
        response = client.delete(
            "/activities/Chess%20Club/participants?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"]
    
    def test_unregister_multiple_times_fails_second_time(self, client, reset_activities):
        """Test that unregistering same participant twice fails on second attempt."""
        email = "michael@mergington.edu"
        
        # First unregister succeeds
        response1 = client.delete(f"/activities/Chess%20Club/participants?email={email}")
        assert response1.status_code == 200
        
        # Second unregister fails
        response2 = client.delete(f"/activities/Chess%20Club/participants?email={email}")
        assert response2.status_code == 404


class TestSignupAndUnregisterFlow:
    """Integration tests for signup + unregister flows."""
    
    def test_signup_then_unregister_flow(self, client, reset_activities):
        """Test complete flow: signup, verify, unregister, verify."""
        email = "integration@mergington.edu"
        activity = "Chess Club"
        
        # Initial state
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Signup
        signup_resp = client.post(f"/activities/{activity.replace(' ', '%20')}/signup?email={email}")
        assert signup_resp.status_code == 200
        
        # Verify added
        response = client.get("/activities")
        after_signup = len(response.json()[activity]["participants"])
        assert after_signup == initial_count + 1
        
        # Unregister
        unreg_resp = client.delete(
            f"/activities/{activity.replace(' ', '%20')}/participants?email={email}"
        )
        assert unreg_resp.status_code == 200
        
        # Verify removed
        response = client.get("/activities")
        after_unreg = len(response.json()[activity]["participants"])
        assert after_unreg == initial_count
    
    def test_multiple_signups_and_unregisters(self, client, reset_activities):
        """Test multiple signup/unregister operations in sequence."""
        activity = "Programming Class"
        emails = ["test1@mergington.edu", "test2@mergington.edu", "test3@mergington.edu"]
        
        # Signup all
        for email in emails:
            response = client.post(f"/activities/{activity.replace(' ', '%20')}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all added
        response = client.get("/activities")
        for email in emails:
            assert email in response.json()[activity]["participants"]
        
        # Unregister first and last
        client.delete(f"/activities/{activity.replace(' ', '%20')}/participants?email={emails[0]}")
        client.delete(f"/activities/{activity.replace(' ', '%20')}/participants?email={emails[2]}")
        
        # Verify correct ones removed
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert emails[0] not in participants
        assert emails[1] in participants
        assert emails[2] not in participants
