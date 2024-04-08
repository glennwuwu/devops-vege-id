FROM python:3.10-slim
#Update packages installed in the image
RUN apt-get update -y
# To fix gcc error during build.
# RUN apt install gcc -y
RUN apt-get install build-essential -y

COPY requirements.txt requirements.txt
#Install all the packages needed to run our web app

RUN apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6 libpq-dev
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
# Add every files and folder into the app folder

#Change our working directory to app folder
WORKDIR /app

COPY ./application /app/application
COPY ./tests /app/tests
COPY ./*.py /app  

# Expose port 8000 for http communication
EXPOSE 8000
# Run gunicorn web server and binds it to the port
CMD gunicorn -w 1 -b 0.0.0.0 app:app