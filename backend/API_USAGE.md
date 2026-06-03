# Frontend API Handoff

Backend base URL:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

The frontend should call the FastAPI backend only. Supabase keys stay inside `backend/.env`.

## 1. Predict Only

Use this when the frontend has only complaint text and wants category plus priority.

```text
POST /api/complaints/predict
```

Request:

```json
{
  "complaint_text": "Street light is not working near my house"
}
```

Response:

```json
{
  "category": "Electricity",
  "priority": "Low",
  "category_confidence": 0.9999,
  "priority_confidence": 0.9986
}
```

Frontend code:

```js
const response = await fetch("http://127.0.0.1:8000/api/complaints/predict", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    complaint_text: complaintText,
  }),
});

const prediction = await response.json();
```

## 2. Register User

Use this before saving complaints. The response gives `user_id`.

```text
POST /api/auth/register
```

Request:

```json
{
  "name": "Rahul Sharma",
  "email": "rahul@example.com",
  "phone_number": "9999999999",
  "password": "password123"
}
```

Response:

```json
{
  "message": "User registered successfully",
  "user": {
    "user_id": 1,
    "name": "Rahul Sharma",
    "email": "rahul@example.com",
    "phone_number": "9999999999",
    "created_at": "2026-06-03T09:30:00"
  }
}
```

## 3. Login User

```text
POST /api/auth/login
```

Request:

```json
{
  "email": "rahul@example.com",
  "password": "password123"
}
```

Response:

```json
{
  "message": "Login successful",
  "user": {
    "user_id": 1,
    "name": "Rahul Sharma",
    "email": "rahul@example.com",
    "phone_number": "9999999999",
    "created_at": "2026-06-03T09:30:00"
  }
}
```

Store `user.user_id` in frontend state/local storage and send it when creating a grievance.

## 4. Create Grievance

This is the main complaint form API. It predicts category/priority and saves to Supabase.

```text
POST /api/complaints/
```

Request:

```json
{
  "complaint_text": "Street light is not working near my house",
  "location": "Kondapur",
  "user_id": 1
}
```

Required fields:

```text
complaint_text
user_id
```

Optional field:

```text
location
```

Response:

```json
{
  "message": "Complaint saved and predicted successfully",
  "grievance": {
    "grievance_id": 2,
    "ticket_number": "PI-20260603-5BD3C4",
    "user_id": 1,
    "department_id": 1,
    "complaint_text": "Street light is not working near my house",
    "location": "Kondapur",
    "priority": "Low",
    "status": "Pending",
    "submission_date": "2026-06-03T09:30:00",
    "resolved_date": null
  },
  "prediction": {
    "category": "Electricity",
    "priority": "Low",
    "category_confidence": 0.9999,
    "priority_confidence": 0.9986
  }
}
```

Frontend code:

```js
const response = await fetch("http://127.0.0.1:8000/api/complaints/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    complaint_text: complaintText,
    location,
    user_id: userId,
  }),
});

const savedComplaint = await response.json();
```

## 5. List Grievances

```text
GET /api/complaints/
```

Optional filters:

```text
GET /api/complaints/?user_id=1
GET /api/complaints/?department_id=2
GET /api/complaints/?status=Pending
```

Response:

```json
[
  {
    "grievance_id": 2,
    "ticket_number": "PI-20260603-5BD3C4",
    "user_id": 1,
    "department_id": 1,
    "complaint_text": "Street light is not working near my house",
    "location": "Kondapur",
    "priority": "Low",
    "status": "Pending",
    "submission_date": "2026-06-03T09:30:00",
    "resolved_date": null
  }
]
```

## 6. Get One Grievance

```text
GET /api/complaints/{grievance_id}
```

Example:

```text
GET /api/complaints/2
```

## 7. Update Grievance Status

```text
PATCH /api/complaints/{grievance_id}/status
```

Request:

```json
{
  "status": "Resolved"
}
```

Allowed frontend values can be:

```text
Pending
In Progress
Resolved
Rejected
```

If status is `Resolved`, backend also fills `resolved_date`.

## 8. Dashboard Summary

```text
GET /api/dashboard/summary
```

Response:

```json
{
  "total_complaints": 10,
  "open_complaints": 8,
  "resolved_complaints": 2,
  "departments": []
}
```

## 9. Departments

```text
GET /api/dashboard/departments
```

```text
POST /api/dashboard/departments
```

Create request:

```json
{
  "department_name": "Water"
}
```

## 10. Users

```text
GET /api/users/
GET /api/users/{user_id}
```

## Frontend Pages Needed

Minimum frontend screens:

```text
Register Page
Login Page
Complaint Form Page
My Complaints Page
Admin/Dashboard Page
Complaint Detail Page
```

Complaint form fields:

```text
complaint_text textarea
location input
submit button
```

After submit, show:

```text
ticket_number
predicted category
predicted priority
status
```
