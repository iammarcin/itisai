FROM python:3.12-slim

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /tmp/requirements.txt
#RUN python -c "import nltk; nltk.download('punkt')"

WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug", "--reload-dir", "/app", "--proxy-headers"]