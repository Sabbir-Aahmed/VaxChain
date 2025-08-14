# VaxChain API

VaxChain is a vaccination management system built with **Django** and **Django REST Framework (DRF)**.  
It provides APIs for managing vaccine campaigns, scheduling vaccinations, booking vaccine slots, and submitting campaign reviews.  
The system supports **role-based access** for **Doctors** and **Patients**, with Swagger UI documentation.

---

## Features
- User management with **Doctor** and **Patient** roles.
- Profile management for doctors and patients.
- CRUD operations for **Vaccine Campaigns** (Doctor only).
- CRUD operations for **Vaccine Schedules** (Doctor only).
- Booking vaccine slots for patients with automatic slot decrementing.
- Campaign reviews from patients.
- Role-based access control.
- Swagger UI for interactive API testing.

---

## Tech Stack

- **Python**
- **Django** - Backend framework
- **Django REST Framework (DRF)** - API development
- **Djoser** - Authentication
- **drf_yasg** - API documentation (Swagger)
- **PostgreSQL / SQLite** - Database

---

## Getting Started

### Prerequisites

- Python 3.8+
- pip
- virtualenv (optional but recommended)
- PostgreSQL or SQLite (default)

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/Sabbir-Aahmed/VaxChain.git
cd phimart
```
**2. Create and activate a virtual environment**

```
python -m venv venv
source venv/bin/activate   
# On Windows:venv\Scripts\activate
```
**3. Install dependencies**

```
pip install -r requirements.txt
```
**4. Configure environment variables**

Create a .env file or set environment variables as needed for:

 - DJANGO_SECRET_KEY

 - Database credentials (if using PostgreSQL)

 - Other settings as needed

**5. Apply migration**
```
python manage.py migrate
```
**6. Create a superuser**
```
python manage.py createsuperuser
```
**7. Run the development server**

```
python manage.py runserver
```
## API Endpoints

### Auth
| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/v1/auth/users/` | POST | Register a new user | Public |
| `/api/v1/auth/users/me/` | GET | Retrieve current user 

### Patient Profiles
| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/v1/patients/` | GET | List patient profile(s) | Patient only |
| `/api/v1/patients/` | POST | Create patient profile | Patient only |
| `/api/v1/patients/{id}/` | GET | Retrieve patient profile | Patient only |
| `/api/v1/patients/{id}/` | PUT | Update patient profile | Patient only |
| `/api/v1/patients/{id}/` | PATCH | Partial update patient profile | Patient only |
| `/api/v1/patients/{id}/` | DELETE | Delete patient profile | Patient only |

### Doctor Profiles
| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/v1/doctors/` | GET | List doctor profile(s) | Doctor only |
| `/api/v1/doctors/` | POST | Create doctor profile | Doctor only |
| `/api/v1/doctors/{id}/` | GET | Retrieve doctor profile | Doctor only |
| `/api/v1/doctors/{id}/` | PUT | Update doctor profile | Doctor only |
| `/api/v1/doctors/{id}/` | PATCH | Partial update doctor profile | Doctor only |
| `/api/v1/doctors/{id}/` | DELETE | Delete doctor profile | Doctor only |

### Vaccine Campaigns
| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/v1/campaigns/` | GET | List vaccine campaigns | Authenticated |
| `/api/v1/campaigns/` | POST | Create a new campaign | Doctor only |
| `/api/v1/campaigns/{id}/` | GET | Retrieve a campaign | Authenticated |
| `/api/v1/campaigns/{id}/` | PUT | Update a campaign | Doctor only |
| `/api/v1/campaigns/{id}/` | PATCH | Partial update campaign | Doctor only |
| `/api/v1/campaigns/{id}/` | DELETE | Delete a campaign | Doctor only |

### Vaccine Schedules
| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/v1/schedules/` | GET | List schedules | Authenticated |
| `/api/v1/schedules/` | POST | Create a schedule | Doctor only |
| `/api/v1/schedules/{id}/` | GET | Retrieve a schedule | Authenticated |
| `/api/v1/schedules/{id}/` | PUT | Update a schedule | Doctor only |
| `/api/v1/schedules/{id}/` | PATCH | Partial update schedule | Doctor only |
| `/api/v1/schedules/{id}/` | DELETE | Delete a schedule | Doctor only |

### Vaccine Bookings
| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/v1/bookings/` | GET | List bookings | Patient & Doctor |
| `/api/v1/bookings/` | POST | Create a booking (first dose) | Patient only |
| `/api/v1/bookings/{id}/` | GET | Retrieve a booking | Patient & Doctor |
| `/api/v1/bookings/{id}/` | DELETE | Cancel a booking | Patient only |

### Campaign Reviews
| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/v1/reviews/` | GET | List reviews (optional `?campaign_id=` filter) | Authenticated |
| `/api/v1/reviews/` | POST | Create a review | Patient only |
| `/api/v1/reviews/{id}/` | GET | Retrieve a review | Authenticated |
| `/api/v1/reviews/{id}/` | PUT | Update a review | Patient only |
| `/api/v1/reviews/{id}/` | PATCH | Partial update a review | Patient only |
| `/api/v1/reviews/{id}/` | DELETE | Delete a review | Patient only |

---

### Example Request

```http
GET /api//v1/products/
Host: localhost:8000
Authorization: Bearer <your_access_token>
Accept: application/json
```

## API Documentation
The interactive Swagger UI is available at:
```
http://localhost:8000/api/v1/swagger/
```

## Environment Variables

Create a `.env` file in your project root with the following variables:

```env
# Django settings
DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL example)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=phimart_db
DB_USER=db_user
DB_PASSWORD=db_password
DB_HOST=localhost
DB_PORT=5432

# JWT token lifetimes (optional)
JWT_ACCESS_TOKEN_LIFETIME=5m
JWT_REFRESH_TOKEN_LIFETIME=1d
```

## License
This project is licensed under the MIT License.

## Contact

Created by **Md Sabbir Ahmed**

- Email: [mdsabbir5820@gmail.com](mailto:mdsabbir5820@gmail.com)   
- LinkedIn: [https://www.linkedin.com/in/md-sabbir-ahmed/](https://www.linkedin.com/in/md-sabbir-ahmed/)  

Feel free to reach out for questions, suggestions, or collaboration!
