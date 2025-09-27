#  Django Helpdesk Ticketing System

A backend API for a simple Helpdesk & Ticket Management System built with **Django** and **Django REST Framework**.

---

##  Features

-  **Role-Based Access Control** (Admin, Agent, Customer)
-  **JWT Authentication** using SimpleJWT
-  **Ticket Lifecycle**: Creation, Assignment, Resolution, Escalation
-  **Commenting System** on tickets
-  **Escalation Engine** with Celery & Celery Beat
-  **Activity Reports**: Tickets stats from the last 7 days
-  **Email Notifications** on escalations (Console backend for demo)

---

##  Installation Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/imc8294/helpdesk_system.git
cd helpdesk_system
```

### 2. Create and Activate Virtual Environment
```bash
# For Linux/macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations 
```bash
python manage.py makemigration
python manage.py migrate
```

### 5. Start Development Server
```bash
python manage.py runserver
```

### 6. Start Celery Worker & Beat (Run in separate terminals)
```bash
# Celery worker (Windows users must use --pool=solo)
celery -A helpdesk_system worker --loglevel=info

# Celery Beat for periodic tasks
celery -A helpdesk_system beat --loglevel=info
```

---

## Authentication (JWT)

JWT is used for securing the API using **djangorestframework-simplejwt**.

###  Endpoints

- `POST /UsersLogin` – Obtain access tokens.
- Tokens must be sent as Bearer tokens in the `Authorization` header.

###  Role-based Permissions

| Role     | Capabilities |
|----------|--------------|
| Admin    | Manage all tickets, assign, escalate, resolve |
| Agent    | Update ticket status, add comments |
| Customer | Create tickets, view own tickets only |

---

##  API Endpoints & Documentation
Swagger/OpenAPI available at:

``` bash 
  http://127.0.0.1:8000
```

---



## Escalation Logic

Tickets are escalated based on their **priority** if not updated within a specified timeframe:

| Priority | Escalation After |
|----------|------------------|
| High     | 1 hour           |
| Medium   | 4 hours          |
| Low      | 24 hours         |

### Escalation Behavior

- Ticket status changes to `Escalated`
- Email notification is sent to:
  - Ticket creator
  - All Admins
- Managed using **Celery** and **Celery Beat**
