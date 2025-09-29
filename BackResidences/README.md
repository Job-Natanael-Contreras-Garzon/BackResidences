# BackResidences Project

## Overview
BackResidences is a Django project designed to manage residential properties, security events, user authentication, payments, and common areas. The project utilizes PostgreSQL as its database backend.

## Features
- User authentication and authorization
- Management of residential properties and their details
- Security event logging and camera management
- Payment processing and debt tracking
- Reservation system for common areas

## Project Structure
```
BackResidences
├── manage.py
├── requirements.txt
├── BackResidences
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps
│   ├── authentication
│   ├── security
│   ├── residences
│   ├── payments
│   └── common_areas
├── static
├── media
└── templates
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd BackResidences
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Configure the PostgreSQL database in `BackResidences/settings.py`.

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```
   python manage.py runserver
   ```

## Usage
- Access the application at `http://127.0.0.1:8000/`.
- Admin panel can be accessed at `http://127.0.0.1:8000/admin/`.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License.