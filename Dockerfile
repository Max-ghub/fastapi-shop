FROM python:3.12-slim AS depends
WORKDIR /app
RUN pip install --no-cache-dir "poetry==1.8.0"
COPY pyproject.toml poetry.lock* ./
RUN poetry export -f requirements.txt --without dev -o requirements.txt

FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=depends /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
