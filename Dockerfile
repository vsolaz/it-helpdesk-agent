FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent/ ./agent/

EXPOSE 8080
ENV FLASK_APP=agent/app.py

CMD ["python", "-m", "flask", "--app", "agent/app", "run", "--host", "0.0.0.0", "--port", "8080"]
