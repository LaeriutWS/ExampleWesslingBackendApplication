# Example of a Django app for WESSLING application (Backend)

This project can be used as a starting point together with the example React application as a starting point for WESSLING projects.

This project already includes the following:

- User authentication (JWT)
- Group and permission management
- Google Login
- Backend Permission management


## Installation

1. Clone the repository
2. Create a virtual environment
3. Install the requirements
4. Run the migrations
5. Create a superuser
6. Run the server

```bash
git clone
cd wessling-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```