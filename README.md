\# Pet Adoption Portal



\*\*Project Owner:\*\* Rohan Uttekar

\*\*Course:\*\* Cloud Computing and DevOps (CSE30040)

\*\*Project:\*\* CCA 2 – Individual Project



\## Project Overview



The Pet Adoption Portal is a Flask-based web application that allows users to browse available pets, add pets for adoption, and submit adoption requests.



\## Features



\* Home page displaying available pets

\* Browse and search available pets

\* Add pets with input validation

\* Submit adoption requests

\* View adoption requests

\* JSON APIs for pets and adoption requests

\* Health-check endpoint

\* Footer displaying the deployed Git commit ID



\## Technologies Used



\* Python and Flask

\* SQLite

\* HTML, CSS and JavaScript

\* Pytest

\* Flake8

\* Docker

\* Git and GitHub Actions

\* Render



\## Run Locally



1\. Clone the repository.



2\. Create and activate a Python virtual environment.



3\. Install dependencies:



&#x20;  `pip install -r requirements.txt`



4\. Start the application:



&#x20;  `python app.py`



5\. Open `http://127.0.0.1:5000` in your browser.



\## Testing



Run automated tests:



`python -m pytest -q`



Run linting:



`python -m flake8 --max-line-length=120 --exclude=venv,.pytest\_cache,\_\_pycache\_\_ .`



\## API Endpoints



| Endpoint         | Description                       |

| ---------------- | --------------------------------- |

| `/health`        | Application health check          |

| `/api/pets`      | Returns pet data in JSON          |

| `/api/adoptions` | Returns adoption requests in JSON |



\## Docker



Build the Docker image:



`docker build -t pet-adoption-portal .`



Run the container:



`docker run -p 5000:5000 pet-adoption-portal`



\## CI/CD



GitHub Actions will run automated tests, linting and Docker checks. Deployment to Render will be triggered from the main branch after the required checks pass.



\## Deployment



\*\*Live URL:\*\* To be added after deployment.



\## Author



Rohan Uttekar

B.Tech – Computer Science and Engineering



