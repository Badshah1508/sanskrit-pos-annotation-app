from fastapi.testclient import TestClient
import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

def get_auth_token(username, password):
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, f"Login failed for {username}: {resp.text}"
    return resp.json()["access_token"]


def test_expert_logins_and_next_sentences():
    """Verify that each expert account loads only sentences within their assigned doc_id range."""
    # User 1 -> doc_id 1 to 1000
    token1 = get_auth_token("user1", "password123")
    res1 = client.get("/api/dataset/sentences/next", headers={"Authorization": f"Bearer {token1}"})
    assert res1.status_code == 200
    doc_id_1 = int(res1.json()["doc_id"])
    assert 1 <= doc_id_1 <= 1000
    assert doc_id_1 == 1

    # User 2 -> doc_id 1001 to 2000
    token2 = get_auth_token("user2", "password123")
    res2 = client.get("/api/dataset/sentences/next", headers={"Authorization": f"Bearer {token2}"})
    assert res2.status_code == 200
    doc_id_2 = int(res2.json()["doc_id"])
    assert 1001 <= doc_id_2 <= 2000
    assert doc_id_2 == 1001

    # User 3 -> doc_id 2001 to 3000
    token3 = get_auth_token("user3", "password123")
    res3 = client.get("/api/dataset/sentences/next", headers={"Authorization": f"Bearer {token3}"})
    assert res3.status_code == 200
    doc_id_3 = int(res3.json()["doc_id"])
    assert 2001 <= doc_id_3 <= 3000
    assert doc_id_3 == 2001

    # User 4 -> doc_id 3001 to 4000
    token4 = get_auth_token("user4", "password123")
    res4 = client.get("/api/dataset/sentences/next", headers={"Authorization": f"Bearer {token4}"})
    assert res4.status_code == 200
    doc_id_4 = int(res4.json()["doc_id"])
    assert 3001 <= doc_id_4 <= 4000
    assert doc_id_4 == 3001

    # User 5 -> doc_id 4001 to 5000 (No sentences exist in 70% queue)
    token5 = get_auth_token("user5", "password123")
    res5 = client.get("/api/dataset/sentences/next", headers={"Authorization": f"Bearer {token5}"})
    assert res5.status_code == 404


def test_security_boundary_enforcement():
    """Verify that experts cannot access, draft, or verify documents outside their assigned doc_id range."""
    token2 = get_auth_token("user2", "password123")
    headers2 = {"Authorization": f"Bearer {token2}"}

    # User 2 attempting to access workspace=user1 must return 403 Forbidden
    res_forbidden_ws = client.get("/api/dataset/sentences/next?workspace=user1", headers=headers2)
    assert res_forbidden_ws.status_code == 403

    # User 2 attempting to view sentence 1_0 (doc_id 1) must return 403 Forbidden
    res_forbidden_get = client.get("/api/dataset/sentences/1_0", headers=headers2)
    assert res_forbidden_get.status_code == 403

    # User 2 attempting to save draft for sentence 1_0 must return 403 Forbidden
    res_forbidden_draft = client.put("/api/annotations/1_0/draft", json={"tokens": [], "note": "hacked"}, headers=headers2)
    assert res_forbidden_draft.status_code == 403

    # User 2 attempting to verify sentence 1_0 must return 403 Forbidden
    res_forbidden_verify = client.post("/api/annotations/1_0/verify", json={"tokens": [], "note": "hacked"}, headers=headers2)
    assert res_forbidden_verify.status_code == 403

    # User 2 fetching sentence within their range (1001_0) must succeed
    res_ok_get = client.get("/api/dataset/sentences/1001_0", headers=headers2)
    assert res_ok_get.status_code == 200
    assert res_ok_get.json()["doc_id"] == "1001"


def test_admin_workspace_switching_and_stats():
    """Verify that administrator can switch to any workspace and receive correct document and sentence counts."""
    admin_token = get_auth_token("admin", "admin123")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Admin selecting user1 -> doc_id 1
    r1 = client.get("/api/dataset/sentences/next?workspace=user1", headers=admin_headers)
    assert r1.status_code == 200
    assert int(r1.json()["doc_id"]) == 1

    # Admin selecting user2 -> doc_id 1001
    r2 = client.get("/api/dataset/sentences/next?workspace=user2", headers=admin_headers)
    assert r2.status_code == 200
    assert int(r2.json()["doc_id"]) == 1001

    # Admin selecting user3 -> doc_id 2001
    r3 = client.get("/api/dataset/sentences/next?workspace=user3", headers=admin_headers)
    assert r3.status_code == 200
    assert int(r3.json()["doc_id"]) == 2001

    # Admin selecting user4 -> doc_id 3001
    r4 = client.get("/api/dataset/sentences/next?workspace=user4", headers=admin_headers)
    assert r4.status_code == 200
    assert int(r4.json()["doc_id"]) == 3001

    # Stats for user1
    s1 = client.get("/api/dataset/stats?workspace=user1", headers=admin_headers).json()
    assert s1["total_documents"] == 1000
    assert s1["total_sentences"] == 2658

    # Stats for user2
    s2 = client.get("/api/dataset/stats?workspace=user2", headers=admin_headers).json()
    assert s2["total_documents"] == 1000
    assert s2["total_sentences"] == 2029

    # Stats for user3
    s3 = client.get("/api/dataset/stats?workspace=user3", headers=admin_headers).json()
    assert s3["total_documents"] == 1000
    assert s3["total_sentences"] == 1611

    # Stats for user4
    s4 = client.get("/api/dataset/stats?workspace=user4", headers=admin_headers).json()
    assert s4["total_documents"] == 597
    assert s4["total_sentences"] == 702

    # Global Admin Overview stats
    s_all = client.get("/api/dataset/stats?workspace=all", headers=admin_headers).json()
    assert s_all["total_documents"] == 3597
    assert s_all["total_sentences"] == 7000


def test_draft_saving_and_verification():
    """Verify that an expert can save a draft and verify a sentence within their assigned range."""
    token2 = get_auth_token("user2", "password123")
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Fetch next sentence for User 2 (should be 1001_0)
    next_res = client.get("/api/dataset/sentences/next", headers=headers2)
    assert next_res.status_code == 200
    sent = next_res.json()
    annotation_id = sent["annotation_id"]
    tokens = sent["tokens"]

    # 1. Save draft with note
    token_inputs = [{"token_id": t["token_id"], "gold_sanskrit_tag": "N", "annotation_note": "test"} for t in tokens]
    draft_res = client.put(
        f"/api/annotations/{annotation_id}/draft",
        json={"tokens": token_inputs, "note": "Draft saved by User 2"},
        headers=headers2
    )
    assert draft_res.status_code == 200
    assert draft_res.json()["status"] == "in_progress"
    assert draft_res.json()["annotation_note"] == "Draft saved by User 2"

    # Next sentence call should now return this draft sentence
    resume_res = client.get("/api/dataset/sentences/next", headers=headers2)
    assert resume_res.status_code == 200
    assert resume_res.json()["annotation_id"] == annotation_id
    assert resume_res.json()["status"] == "in_progress"

