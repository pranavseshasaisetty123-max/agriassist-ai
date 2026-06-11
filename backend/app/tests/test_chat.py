from fastapi import status


def _get_token(client, email):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "first_name": "Test",
            "last_name": "Farmer"
        }
    )
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password123"}
    )
    return login_response.json()["access_token"]


def test_create_chat_session(client):
    token = _get_token(client, "session@example.com")
    
    response = client.post(
        "/api/v1/chat/sessions",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Soil Quality Query"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Soil Quality Query"
    assert "id" in data


def test_list_chat_sessions(client):
    token = _get_token(client, "list@example.com")
    
    # Create two sessions
    client.post(
        "/api/v1/chat/sessions",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Session 1"}
    )
    client.post(
        "/api/v1/chat/sessions",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Session 2"}
    )
    
    response = client.get(
        "/api/v1/chat/sessions",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Session 2"  # Sorted desc by updated_at


def test_send_and_retrieve_messages(client):
    token = _get_token(client, "chat@example.com")
    
    # Create session
    session_response = client.post(
        "/api/v1/chat/sessions",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Pest Control"}
    )
    session_id = session_response.json()["id"]
    
    # Fetch messages (initially empty)
    msg_response = client.get(
        f"/api/v1/chat/sessions/{session_id}/messages",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert msg_response.status_code == status.HTTP_200_OK
    assert len(msg_response.json()) == 0
    
    # Send message (triggers mock AI response since no key set)
    post_response = client.post(
        f"/api/v1/chat/sessions/{session_id}/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={"message_text": "What is the best way to handle aphids?"}
    )
    assert post_response.status_code == status.HTTP_200_OK
    post_data = post_response.json()
    assert post_data["user_message"]["message_text"] == "What is the best way to handle aphids?"
    assert post_data["user_message"]["sender"] == "FARMER"
    assert "aphids" in post_data["ai_response"]["message_text"]
    assert post_data["ai_response"]["sender"] == "AI"
    
    # Fetch messages again (now has 2 messages)
    msg_response = client.get(
        f"/api/v1/chat/sessions/{session_id}/messages",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert msg_response.status_code == status.HTTP_200_OK
    msg_data = msg_response.json()
    assert len(msg_data) == 2
    assert msg_data[0]["sender"] == "FARMER"
    assert msg_data[1]["sender"] == "AI"


def test_unauthorized_session_access(client):
    token1 = _get_token(client, "farmer1@example.com")
    token2 = _get_token(client, "farmer2@example.com")
    
    # Farmer 1 creates session
    session_response = client.post(
        "/api/v1/chat/sessions",
        headers={"Authorization": f"Bearer {token1}"},
        json={"title": "Farmer 1 Session"}
    )
    session_id = session_response.json()["id"]
    
    # Farmer 2 tries to access
    response = client.get(
        f"/api/v1/chat/sessions/{session_id}/messages",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Farmer 2 tries to post message
    response = client.post(
        f"/api/v1/chat/sessions/{session_id}/messages",
        headers={"Authorization": f"Bearer {token2}"},
        json={"message_text": "Hello"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
