"""
Walk through every single process, one by one.
"""
import requests
import json
import time

BASE = "http://127.0.0.1:8002/api"
FRONTEND = "http://localhost:3002"
step = [0]

def header(title):
    step[0] += 1
    print(f"\n{'='*60}")
    print(f"  STEP {step[0]}: {title}")
    print(f"{'='*60}")

def show(label, r):
    status = r.status_code
    body = None
    try:
        body = r.json()
        body_str = json.dumps(body, indent=2)
        if len(body_str) > 500:
            body_str = body_str[:500] + "\n  ... (truncated)"
    except:
        body_str = r.text[:300] if hasattr(r, 'text') else str(status)
    tag = "OK" if 200 <= status < 400 else f"FAIL({status})"
    print(f"  [{tag}] {label}")
    print(f"  Response: {body_str}")
    return body or {}

def show_status(label, r):
    tag = "OK" if 200 <= r.status_code < 400 else f"FAIL({r.status_code})"
    print(f"  [{tag}] {label} -> {r.status_code}")

# ================================================================
header("PUBLIC — Health Check")
# ================================================================
r = requests.get(f"{BASE}/health/")
show("GET /api/health/", r)

# ================================================================
header("PUBLIC — Get CSRF Token")
# ================================================================
s = requests.Session()
r = s.get(f"{BASE}/csrf/")
data = show("GET /api/csrf/", r)
csrf = data.get("csrfToken", "")
print(f"  Token: {csrf[:20]}...")

# ================================================================
header("PUBLIC — List Programs (no auth)")
# ================================================================
r = requests.get(f"{BASE}/programs/")
data = show("GET /api/programs/", r)
print(f"  Programs: {len(data.get('programs', []))}")
print(f"  Categories: {len(data.get('categories', []))}")

# ================================================================
header("SIGNUP — Corps Member (missing fields)")
# ================================================================
r = s.post(f"{BASE}/auth/signup/", json={
    "fullName": "Incomplete User",
    "email": "incomplete@test.com",
    "password": "Pass1234!"
}, headers={"X-CSRFToken": csrf, "Content-Type": "application/json"})
show("POST /api/auth/signup/ (missing fields)", r)

# ================================================================
header("SIGNUP — Corps Member (full)")
# ================================================================
r = s.post(f"{BASE}/auth/signup/", json={
    "fullName": "Adamu Bello",
    "email": f"adamu_{int(time.time())}@test.com",
    "password": "Pass1234!",
    "username": f"adamu_{int(time.time())}",
    "phone": "08031234567",
    "role": "corps_member",
    "nyscStateCode": "FC/20/456",
    "stateOfDeployment": "Abuja",
    "stateOfOrigin": "Kaduna",
    "lgaOfDeployment": "Gwagwalada",
    "skillInterest": "Welding"
}, headers={"X-CSRFToken": csrf, "Content-Type": "application/json"})
data = show("POST /api/auth/signup/ (corps member)", r)
cm_email = data.get("user", {}).get("email", "")

# ================================================================
header("SIGNUP — Duplicate (same email)")
# ================================================================
r = s.post(f"{BASE}/auth/signup/", json={
    "fullName": "Dup User",
    "email": cm_email,
    "password": "Pass1234!",
    "username": "dup_user",
    "phone": "08099999999",
    "role": "corps_member"
}, headers={"X-CSRFToken": s.cookies.get("csrftoken", ""), "Content-Type": "application/json"})
show("POST /api/auth/signup/ (duplicate)", r)

# ================================================================
header("LOGIN — Corps Member")
# ================================================================
s_cm = requests.Session()
s_cm.get(f"{BASE}/csrf/")
csrf_cm = s_cm.cookies.get("csrftoken", "")
r = s_cm.post(f"{BASE}/auth/login/", json={
    "email": "corper@test.com",
    "password": "Pass1234!"
}, headers={"X-CSRFToken": csrf_cm, "Content-Type": "application/json"})
show("POST /api/auth/login/ (corper@test.com)", r)

# ================================================================
header("GET /me — Verify logged in")
# ================================================================
r = s_cm.get(f"{BASE}/auth/me/")
show("GET /api/auth/me/ (as corper)", r)

# ================================================================
header("DASHBOARD — Corps Member")
# ================================================================
r = s_cm.get(f"{BASE}/dashboard/")
show("GET /api/dashboard/ (corper)", r)

# ================================================================
header("PROGRAMS — List (authenticated)")
# ================================================================
r = s_cm.get(f"{BASE}/programs/")
data = show("GET /api/programs/ (corper)", r)
print(f"  Programs: {len(data.get('programs', []))}")

# ================================================================
header("APPLICATIONS — List (corper)")
# ================================================================
r = s_cm.get(f"{BASE}/applications/")
show("GET /api/applications/ (corper)", r)

# ================================================================
header("TRAINERS — List available trainers")
# ================================================================
r = s_cm.get(f"{BASE}/trainers/")
show("GET /api/trainers/ (corper)", r)

# ================================================================
header("MY TRAINERS — List")
# ================================================================
r = s_cm.get(f"{BASE}/my-trainers/")
show("GET /api/my-trainers/ (corper)", r)

# ================================================================
header("CONNECTIONS — List")
# ================================================================
r = s_cm.get(f"{BASE}/connections/")
show("GET /api/connections/ (corper)", r)

# ================================================================
header("NOTIFICATIONS — List")
# ================================================================
r = s_cm.get(f"{BASE}/notifications/")
show("GET /api/notifications/ (corper)", r)

# ================================================================
header("FAST TRACK — Trainee courses")
# ================================================================
r = s_cm.get(f"{BASE}/trainee/fast-track-courses/")
show("GET /api/trainee/fast-track-courses/ (corper)", r)

# ================================================================
header("COMPLAINT — Submit")
# ================================================================
r = s_cm.post(f"{BASE}/submit-complaint/", json={
    "subject": "Test complaint",
    "message": "This is a test complaint about the program."
}, headers={"X-CSRFToken": s_cm.cookies.get("csrftoken", ""), "Content-Type": "application/json"})
show("POST /api/submit-complaint/ (corper)", r)

# ================================================================
header("NOTIFICATIONS — Mark all read")
# ================================================================
r = s_cm.post(f"{BASE}/notifications/read-all/", json={},
    headers={"X-CSRFToken": s_cm.cookies.get("csrftoken", ""), "Content-Type": "application/json"})
show("POST /api/notifications/read-all/ (corper)", r)

# ================================================================
header("LOGOUT — Corps Member")
# ================================================================
r = s_cm.post(f"{BASE}/auth/logout/", json={},
    headers={"X-CSRFToken": s_cm.cookies.get("csrftoken", ""), "Content-Type": "application/json"})
show("POST /api/auth/logout/", r)

r = s_cm.get(f"{BASE}/auth/me/")
show("GET /api/auth/me/ (after logout)", r)

# ================================================================
header("LOGIN — Trainer")
# ================================================================
s_tr = requests.Session()
s_tr.get(f"{BASE}/csrf/")
csrf_tr = s_tr.cookies.get("csrftoken", "")
r = s_tr.post(f"{BASE}/auth/login/", json={
    "email": "trainer@test.com",
    "password": "Pass1234!"
}, headers={"X-CSRFToken": csrf_tr, "Content-Type": "application/json"})
show("POST /api/auth/login/ (trainer@test.com)", r)

# ================================================================
header("GET /me — Verify trainer")
# ================================================================
r = s_tr.get(f"{BASE}/auth/me/")
show("GET /api/auth/me/ (as trainer)", r)

# ================================================================
header("DASHBOARD — Trainer")
# ================================================================
r = s_tr.get(f"{BASE}/dashboard/")
show("GET /api/dashboard/ (trainer)", r)

# ================================================================
header("MANAGE COURSES — Trainer lists courses")
# ================================================================
r = s_tr.get(f"{BASE}/manage/courses/")
show("GET /api/manage/courses/ (trainer)", r)

# ================================================================
header("MANAGE COURSES — Trainer creates course")
# ================================================================
csrf_tr = s_tr.cookies.get("csrftoken", "")
r = s_tr.post(f"{BASE}/manage/courses/", json={
    "title": "Advanced Welding Techniques",
    "description": "Master MIG, TIG, and stick welding",
    "category": "construction",
    "price": "75000",
    "durationWeeks": 6,
    "maxStudents": 15,
    "startDate": "2026-08-01",
    "endDate": "2026-09-12"
}, headers={"X-CSRFToken": csrf_tr, "Content-Type": "application/json"})
data = show("POST /api/manage/courses/ (create course)", r)
course_id = data.get("course", {}).get("id", 0)
print(f"  Created course ID: {course_id}")

# ================================================================
header("COURSE DETAIL — View created course")
# ================================================================
r = s_tr.get(f"{BASE}/courses/{course_id}/")
show(f"GET /api/courses/{course_id}/ (detail)", r)

# ================================================================
header("MANAGE FAST TRACK VIDEOS — Trainer lists")
# ================================================================
r = s_tr.get(f"{BASE}/manage/fast-track-videos/")
show("GET /api/manage/fast-track-videos/ (trainer)", r)

# ================================================================
header("TRAINER CORPERS — List")
# ================================================================
r = s_tr.get(f"{BASE}/trainer/corpers/")
show("GET /api/trainer/corpers/", r)

# ================================================================
header("TRAINER ENROLLMENTS — Pending")
# ================================================================
r = s_tr.get(f"{BASE}/trainer/enrollments/pending/")
show("GET /api/trainer/enrollments/pending/", r)

# ================================================================
header("TRAINER NOTIFICATIONS — List")
# ================================================================
r = s_tr.get(f"{BASE}/notifications/")
show("GET /api/notifications/ (trainer)", r)

# ================================================================
header("LOGOUT — Trainer")
# ================================================================
r = s_tr.post(f"{BASE}/auth/logout/", json={},
    headers={"X-CSRFToken": s_tr.cookies.get("csrftoken", ""), "Content-Type": "application/json"})
show("POST /api/auth/logout/ (trainer)", r)

# ================================================================
header("LOGIN — SAED Admin")
# ================================================================
s_ad = requests.Session()
s_ad.get(f"{BASE}/csrf/")
csrf_ad = s_ad.cookies.get("csrftoken", "")
r = s_ad.post(f"{BASE}/auth/login/", json={
    "email": "admin@test.com",
    "password": "Pass1234!"
}, headers={"X-CSRFToken": csrf_ad, "Content-Type": "application/json"})
show("POST /api/auth/login/ (admin@test.com)", r)

# ================================================================
header("GET /me — Verify admin")
# ================================================================
r = s_ad.get(f"{BASE}/auth/me/")
show("GET /api/auth/me/ (as admin)", r)

# ================================================================
header("DASHBOARD — Admin")
# ================================================================
r = s_ad.get(f"{BASE}/dashboard/")
show("GET /api/dashboard/ (admin)", r)

# ================================================================
header("MANAGE USERS — Admin lists all users")
# ================================================================
r = s_ad.get(f"{BASE}/manage/users/")
data = show("GET /api/manage/users/ (admin)", r)
print(f"  Total users: {len(data.get('users', []))}")

# ================================================================
header("MANAGE PROGRAMS — Admin lists programs")
# ================================================================
r = s_ad.get(f"{BASE}/manage/programs/")
show("GET /api/manage/programs/ (admin)", r)

# ================================================================
header("MANAGE APPLICATIONS — Admin lists applications")
# ================================================================
r = s_ad.get(f"{BASE}/manage/applications/")
show("GET /api/manage/applications/ (admin)", r)

# ================================================================
header("ADMIN COURSES — Admin lists all courses")
# ================================================================
r = s_ad.get(f"{BASE}/admin/courses/")
show("GET /api/admin/courses/ (admin)", r)

# ================================================================
header("ADMIN REFUNDS — Pending")
# ================================================================
r = s_ad.get(f"{BASE}/admin/refunds/pending/")
show("GET /api/admin/refunds/pending/ (admin)", r)

# ================================================================
header("ADMIN NOTIFICATIONS")
# ================================================================
r = s_ad.get(f"{BASE}/notifications/")
show("GET /api/notifications/ (admin)", r)

# ================================================================
header("LOGOUT — Admin")
# ================================================================
r = s_ad.post(f"{BASE}/auth/logout/", json={},
    headers={"X-CSRFToken": s_ad.cookies.get("csrftoken", ""), "Content-Type": "application/json"})
show("POST /api/auth/logout/ (admin)", r)

# ================================================================
header("LOGIN — DUNIS Admin")
# ================================================================
s_du = requests.Session()
s_du.get(f"{BASE}/csrf/")
csrf_du = s_du.cookies.get("csrftoken", "")
r = s_du.post(f"{BASE}/auth/login/", json={
    "email": "dunis@test.com",
    "password": "Pass1234!"
}, headers={"X-CSRFToken": csrf_du, "Content-Type": "application/json"})
show("POST /api/auth/login/ (dunis@test.com)", r)

# ================================================================
header("GET /me — Verify DUNIS admin")
# ================================================================
r = s_du.get(f"{BASE}/auth/me/")
show("GET /api/auth/me/ (as dunis)", r)

# ================================================================
header("DUNIS — Pending payments")
# ================================================================
r = s_du.get(f"{BASE}/dunis/pending-payments/")
show("GET /api/dunis/pending-payments/", r)

# ================================================================
header("DUNIS — All trainers")
# ================================================================
r = s_du.get(f"{BASE}/dunis/trainers/")
show("GET /api/dunis/trainers/", r)

# ================================================================
header("DUNIS — Manage programs")
# ================================================================
r = s_du.get(f"{BASE}/manage/programs/")
show("GET /api/manage/programs/ (dunis)", r)

# ================================================================
header("DUNIS — Manage users")
# ================================================================
r = s_du.get(f"{BASE}/manage/users/")
show("GET /api/manage/users/ (dunis)", r)

# ================================================================
header("DUNIS — Notifications")
# ================================================================
r = s_du.get(f"{BASE}/notifications/")
show("GET /api/notifications/ (dunis)", r)

# ================================================================
header("LOGOUT — DUNIS Admin")
# ================================================================
r = s_du.post(f"{BASE}/auth/logout/", json={},
    headers={"X-CSRFToken": s_du.cookies.get("csrftoken", ""), "Content-Type": "application/json"})
show("POST /api/auth/logout/ (dunis)", r)

# ================================================================
header("PASSWORD RESET — Request")
# ================================================================
s2 = requests.Session()
s2.get(f"{BASE}/csrf/")
csrf2 = s2.cookies.get("csrftoken", "")
r = s2.post(f"{BASE}/auth/password-reset/", json={
    "email": "corper@test.com"
}, headers={"X-CSRFToken": csrf2, "Content-Type": "application/json"})
data = show("POST /api/auth/password-reset/", r)
uid = data.get("uid", "")
token = data.get("token", "")
print(f"  UID: {uid}, Token: {token[:20]}...")

# ================================================================
header("PASSWORD RESET — Confirm with bad token")
# ================================================================
r = s2.post(f"{BASE}/auth/password-reset/confirm/", json={
    "uid": uid,
    "token": "badtoken123",
    "new_password": "NewPass1234!"
}, headers={"X-CSRFToken": s2.cookies.get("csrftoken", ""), "Content-Type": "application/json"})
show("POST /api/auth/password-reset/confirm/ (bad token)", r)

# ================================================================
header("EMAIL — Verify endpoint exists")
# ================================================================
r = s2.post(f"{BASE}/auth/email-verify/", json={
    "uid": uid,
    "token": "testtoken"
}, headers={"X-CSRFToken": s2.cookies.get("csrftoken", ""), "Content-Type": "application/json"})
show("POST /api/auth/email-verify/ (test token)", r)

# ================================================================
header("PAYSTACK — Initialize payment")
# ================================================================
s_pay = requests.Session()
s_pay.get(f"{BASE}/csrf/")
csrf_pay = s_pay.cookies.get("csrftoken", "")
r = s_pay.post(f"{BASE}/auth/login/", json={
    "email": "corper@test.com",
    "password": "Pass1234!"
}, headers={"X-CSRFToken": csrf_pay, "Content-Type": "application/json"})
csrf_pay = s_pay.cookies.get("csrftoken", "")
r = s_pay.post(f"{BASE}/paystack/initialize/", json={
    "email": "corper@test.com"
}, headers={"X-CSRFToken": csrf_pay, "Content-Type": "application/json"})
show("POST /api/paystack/initialize/", r)

# ================================================================
header("COURSE PAY — Initialize")
# ================================================================
r = s_pay.post(f"{BASE}/courses/pay/", json={
    "courseId": 1
}, headers={"X-CSRFToken": s_pay.cookies.get("csrftoken", ""), "Content-Type": "application/json"})
show("POST /api/courses/pay/ (initialize)", r)

# ================================================================
header("COURSE PAY — Verify (test reference)")
# ================================================================
r = s_pay.post(f"{BASE}/courses/pay/verify/", json={
    "reference": "test_ref_123"
}, headers={"X-CSRFToken": s_pay.cookies.get("csrftoken", ""), "Content-Type": "application/json"})
show("POST /api/courses/pay/verify/", r)

# ================================================================
header("COURSE ENROLLMENT STATUS")
# ================================================================
r = s_pay.get(f"{BASE}/courses/1/enrollment-status/")
show("GET /api/courses/1/enrollment-status/", r)

# ================================================================
header("UPDATE PROFILE — Change bio")
# ================================================================
r = s_pay.patch(f"{BASE}/auth/update-profile/", json={
    "bio": "Updated bio from E2E walkthrough"
}, headers={"X-CSRFToken": s_pay.cookies.get("csrftoken", ""), "Content-Type": "application/json"})
show("PATCH /api/auth/update-profile/", r)

# ================================================================
header("UNAUTHENTICATED — All protected endpoints denied")
# ================================================================
unauth = requests.Session()
for ep in ["auth/me/", "applications/", "trainers/", "dashboard/",
           "notifications/", "connections/", "my-trainers/",
           "manage/users/", "manage/programs/", "manage/courses/",
           "admin/courses/", "manage/fast-track-videos/",
           "trainer/corpers/", "trainer/enrollments/pending/",
           "admin/refunds/pending/", "dunis/pending-payments/",
           "dunis/trainers/", "paystack/initialize/", "courses/pay/",
           "submit-complaint/"]:
    r = unauth.get(f"{BASE}/{ep}")
    tag = "DENIED" if r.status_code in [403, 401] else f"LEAKED({r.status_code})"
    print(f"  [{tag}] GET /api/{ep}")

# ================================================================
header("PERMISSION DENIALS — Wrong roles on wrong endpoints")
# ================================================================
# Corper cannot access admin endpoints
s_cm2 = requests.Session()
s_cm2.get(f"{BASE}/csrf/")
s_cm2.post(f"{BASE}/auth/login/", json={"email": "corper@test.com", "password": "Pass1234!"},
    headers={"X-CSRFToken": s_cm2.cookies.get("csrftoken", ""), "Content-Type": "application/json"})
for ep in ["manage/users/", "manage/programs/", "manage/courses/",
           "admin/courses/", "admin/refunds/pending/",
           "dunis/pending-payments/", "dunis/trainers/"]:
    r = s_cm2.get(f"{BASE}/{ep}")
    tag = "DENIED" if r.status_code in [403, 405] else f"LEAKED({r.status_code})"
    print(f"  [{tag}] Corper -> GET /api/{ep}")

# ================================================================
header("FRONTEND — SPA routes render")
# ================================================================
for path in ["/", "/login", "/signup", "/programs", "/forgot-password",
             "/inactive-account", "/trainer-signup-success", "/admin"]:
    r = requests.get(f"{FRONTEND}{path}", headers={"Accept": "text/html"}, timeout=10)
    tag = "OK" if r.ok and len(r.text) > 100 else f"FAIL({r.status_code})"
    print(f"  [{tag}] {path} ({len(r.text)} bytes)")

# ================================================================
header("FRONTEND PROXY — API through frontend")
# ================================================================
for ep in ["api/health/", "api/programs/"]:
    r = requests.get(f"{FRONTEND}/{ep}", timeout=10)
    tag = "OK" if r.ok else f"FAIL({r.status_code})"
    print(f"  [{tag}] {FRONTEND}/{ep}")

# ================================================================
print(f"\n{'='*60}")
print(f"  WALKTHROUGH COMPLETE — {step[0]} processes verified")
print(f"{'='*60}")
