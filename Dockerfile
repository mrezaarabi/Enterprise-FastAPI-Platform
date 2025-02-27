FROM python:3.11-slim as requirements-stage

WORKDIR /tmp

COPY ./pyproject.toml ./

RUN pip install poetry

# Install the poetry-plugin-export plugin
RUN poetry self add poetry-plugin-export

RUN poetry export -f requirements.txt -o requirements.txt --without-hashes


FROM python:3.11-slim

WORKDIR /app

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Create non-root user for security
RUN adduser --disabled-password --gecos "" appuser

# Create necessary directories
RUN mkdir -p /app/logs
RUN chown -R appuser:appuser /app

COPY --chown=appuser:appuser . /app/

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]