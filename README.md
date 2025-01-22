# FYP Management System

## Overview
The FYP Management System is a web-based platform designed to streamline and simplify the management of Final Year Projects (FYP). The system supports functionalities such as scheduling, evaluations, group creation, and more. The project is divided into two repositories:

1. **Frontend:** Built using React.
2. **Backend:** Built using Django.

## Features

### General Features:
- **Scheduling**: Create and manage schedules for FYP activities.
- **Evaluations**: Conduct and record evaluations for FYP groups.
- **Group Management**: Create and manage groups for FYP projects.
- **User Management**: Role-based access control for Admins, Faculty, and Students.

### Additional Features:
- Interactive dashboard for admins and faculty.
- Dynamic data visualization for progress tracking.

## Tech Stack

### Frontend:
- React
- React Router
- Axios
- Chart.js (for data visualization)
- Tailwind CSS / Material-UI (for styling)

### Backend:
- Django
- Django REST Framework (DRF) for API
- liteSQL


## Setup Instructions

### Prerequisites
- Node.js
- Python 3.8+
- Git

### Backend Setup
1. Clone the backend repository:
   ```bash
   git clone
   ```
2. Create a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Start the backend server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup
1. Clone the frontend repository:
   ```bash
   git clone 
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
4. Start the development server:
   ```bash
   npm start
   ```

## Project Structure

### Frontend:
- `src/components`: Reusable React components.
- `src/pages`: Page-specific components.
- `src/services`: API service integrations.
- `src/styles`: CSS and styling files.

### Backend:
- `fyp/`: Main Django app.
- `fyp/models.py`: Database models.
- `fyp/serializers.py`: API serializers.
- `fyp/views.py`: API views.
- `fyp/urls.py`: URL routing.
- `settings.py`: Project settings and configurations.

## API Endpoints

### Authentication:
- `POST /api/auth/login/`: User login.
- `POST /api/auth/register/`: User registration.


## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature/bug fix.
3. Commit your changes and push them to your fork.
4. Submit a pull request.


