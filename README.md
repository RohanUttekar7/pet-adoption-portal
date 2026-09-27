# Pet Adoption Portal

**Project Owner:** Rohan Uttekar
**PRN:** 1272250909
**Course:** Cloud Computing and DevOps (CSE30040)
**Project:** CCA 2 – Individual Project

## Project Overview

The Pet Adoption Portal is a Flask-based web application that allows users to browse available pets, add pets for adoption, and submit adoption requests. It uses SQLite for data storage and includes automated testing, Docker support, and CI/CD deployment.

## Features

* Home page displaying available pets
* Browse and search available pets
* Add pets with input validation
* Submit adoption requests
* View adoption requests
* JSON APIs for pets and adoption requests
* Health-check endpoint
* Footer displaying the deployed Git commit ID

## Technologies Used

* Python and Flask
* SQLite
* HTML, CSS and JavaScript
* Pytest
* Flake8
* Docker
* Git and GitHub Actions
* Render

## Run Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/RohanUttekar7/pet-adoption-portal.git
   ```

2. Navigate to the project directory:

   ```bash
   cd pet-adoption-portal
   ```

3. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment on Windows:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Start the application:

   ```bash
   python app.py
   ```

7. Open the application in your browser:

   `http://127.0.0.1:5000`

## Testing

Run the automated tests:

```bash
python -m pytest -q
```

Run linting with Flake8:

```bash
python -m flake8 --max-line-length=120 --exclude=venv,.pytest_cache,__pycache__ .
```

## API Endpoints

| Endpoint         | Description                       |
| ---------------- | --------------------------------- |
| `/health`        | Application health check          |
| `/api/pets`      | Returns pet data in JSON          |
| `/api/adoptions` | Returns adoption requests in JSON |

## Docker

Build the Docker image:

```bash
docker build -t pet-adoption-portal .
```

Run the container:

```bash
docker run -p 5000:5000 pet-adoption-portal
```

Open `http://127.0.0.1:5000` to access the application.

## CI/CD

GitHub Actions automates the following tasks:

* Runs automated tests using Pytest.
* Checks code quality using Flake8.
* Builds the Docker image and performs a smoke test.
* Deploys the application to Render when the required checks pass on the main branch.

## Deployment

**Live Application:** https://pet-adoption-portal-phb1.onrender.com

**GitHub Repository:** https://github.com/RohanUttekar7/pet-adoption-portal

## Author

**Rohan Uttekar**
B.Tech – Computer Science and Engineering
