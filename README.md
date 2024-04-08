# Vegetable Prediction Web App

Hi! This project was created as my submission in my "DevOps for Automation and AI" module at Singapore Polytechnic. The main focus of this project was on showcasing DevOps techniques through GitLab CI/CD pipelines, containerisation with Docker, and more along with MLOps with Tensorflow Serving deployed to the web. 

This project is hosted on Render.com, check it out [here!](https://devops-ca2.glennwu.com/)

## Site Overview

![image](https://github.com/glennwuwu/devops-vege-id/assets/22255356/9088286b-5843-4d64-b626-162859f069ce)
*Image upload page*

![image](https://github.com/glennwuwu/devops-vege-id/assets/22255356/529b6239-aca5-43ea-8302-2ef43bd3835d)
*History page with pagination*

![image](https://github.com/glennwuwu/devops-vege-id/assets/22255356/839fa901-123a-43c5-9b8b-8c90cda1b37a)
*Prediction details page*

## Tech Stack
* Backend - Flask: A lightweight and flexible Python web framework.
* Frontend - HTML, Tailwind CSS: HTML for structure, Tailwind CSS for styling.
* Machine Learning - TensorFlow with TensorFlow Serving: Models are developed using TensorFlow and served using TensorFlow Serving for efficient deployment.
* Database - PostgreSQL on Render.com: User and model-related information is stored in a PostgreSQL database hosted on Render.com.
* Web Server - Hosted on Render.com: The web server is hosted on Render.com, providing a platform for deploying and scaling web applications.

### Other Technologies Used
* End-to-end Testing - Selenium: A script is ran within the deployment pipeline to ensure that the site is working as expected.
* Unit Testing - PyTest

## Usage Instructions

### Build Docker Image
Build the Docker image for the project:

```bash
docker build -t ca2:latest .
```

### Run Docker Container
Run the Docker container:

```bash
docker run ca2:latest --name bonk-choy
```

### Run Tests
Run tests with the following commands:

For regular tests:

```bash
FLASK_ENV=testing python -m pytest -m "not rpa"
```

For RPA (Robotic Process Automation) tests:

```bash
docker run -d -p 4444:4444 -p 7900:7900 --name selenium-chrome --shm-size=2g selenium/standalone-chrome
```

```bash
docker run -d -p 4444:4444 -p 7900:7900 --name selenium-edge --shm-size=2g selenium/standalone-edge
```

<!-- ```bash
docker run -d -p 4444:4444 -p 7900:7900 --name selenium-firefox --shm-size=2g selenium/standalone-firefox
``` -->

```bash
FLASK_ENV=testing python -m pytest -m rpa --loc=local --browser=chrome
```

```bash
FLASK_ENV=testing python -m pytest -m rpa --loc=local --browser=edge
```

<!-- ```bash
FLASK_ENV=testing python -m pytest -m rpa --loc=local --browser=firefox
``` -->

## Dependencies

```bash
pip install -r requirements.txt
```

## Contributors

- Glenn Wu

## License

This project is licensed under the [MIT License](LICENSE).
