pare34343434nt@example.com
SecurePass123

{
  "email": "vaishnavi@example.com",
  "password": "Vaishnavi@1234"
}


token

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXJlbnRfaWQiOiI1dlJIOEZvTGo5ZVpNWGtFeEFGb3FHZWFyQ3kyIiwiaWF0IjoxNzY0ODMyMzk3LCJleHAiOjE3NjQ5MTg3OTcsInR5cGUiOiJhY2Nlc3MiLCJlbWFpbCI6InZhaXNobmF2aUBleGFtcGxlLmNvbSJ9.P95klg3nAXO3FzQt41jOdiKQ_WBUF5b1V_F6EGEshWc",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXJlbnRfaWQiOiI1dlJIOEZvTGo5ZVpNWGtFeEFGb3FHZWFyQ3kyIiwiaWF0IjoxNzY0ODMyMzk3LCJleHAiOjE3Njc0MjQzOTcsInR5cGUiOiJyZWZyZXNoIn0.LVZB84hNfsnwpRXFxK6cWQRaVkt_XOu2gCG2wPrA_I0",
  "parent_id": "5vRH8FoLj9eZMXkExAFoqGearCy2",
  "email": "vaishnavi@example.com",
  "phone": null,
  "expires_in": 86400,
  "student_id": null,
  "child_id": null,
  "username": null,
  "name": null,
  "is_student": false,
  "message": null
}

pref

{
  "parent_id": "5vRH8FoLj9eZMXkExAFoqGearCy2",
  "language": "en",
  "email_notifications": true,
  "sms_notifications": true,
  "push_notifications": true,
  "teaching_involvement": "medium",
  "created_at": "2025-12-04T12:44:58.577000Z",
  "updated_at": "2025-12-04T12:44:58.577000Z"
}


child profile

{
  "child_id": "child_ad67a8687a6b",
  "parent_id": "5vRH8FoLj9eZMXkExAFoqGearCy2",
  "name": "Rahul",
  "age": 16,
  "grade": 11,
  "current_level": "intermediate",
  "username": "rahul",
  "created_at": "2025-12-04T12:47:44.914000Z",
  "updated_at": "2025-12-04T12:47:44.914000Z"
}


exam selelction

{
  "child_id": "child_ad67a8687a6b",
  "exam_type": "JEE_MAIN",
  "exam_date": "2026-01-15T00:00:00Z",
  "subject_preferences": {
    "Chemistry": 30,
    "Mathematics": 35,
    "Physics": 35
  },
  "days_until_exam": 42,
  "diagnostic_test_id": "test_3dbb5ea0fc72",
  "created_at": "2025-12-04T12:49:20.391000Z"
}



Registered a new user using POST /api/auth/register/simple
Logged in to get an access token using POST /api/auth/login/email
Sent a verification code using POST /verify/email/send (which requires authentication)
Finally confirmed the email using POST /verify/email/confirm