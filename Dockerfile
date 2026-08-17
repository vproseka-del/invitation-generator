FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ARG BUILD_ID=1
RUN echo "Build ${BUILD_ID}" > /tmp/build_info

COPY . .

EXPOSE 8080

CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:8080", "--timeout", "60"]
