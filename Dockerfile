# Build
FROM python:3.12-slim AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix /install -r requirements.txt

# Runtime
FROM python:3.12-slim AS runtime

ARG USER=api
ARG UID=1001
ENV PYTHONUNBUFFERED=1 PORT=8000

RUN adduser --disabled-password --uid "${UID}" "${USER}"

COPY --from=builder /install /usr/local

WORKDIR /app
COPY . .

USER ${USER}
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]
