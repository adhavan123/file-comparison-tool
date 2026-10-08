FROM python:3.12

WORKDIR /app

COPY . .

RUN apt update -y

RUN apt install pip -y 

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]