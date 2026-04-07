# -------------------------
# BASE IMAGE
# -------------------------
FROM python:3.10-slim

# -------------------------
# WORKDIR
# -------------------------
WORKDIR /app

# -------------------------
# COPY FILES
# -------------------------
COPY . /app

# -------------------------
# INSTALL DEPENDENCIES
# -------------------------
RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    requests \
    numpy

# -------------------------
# ENV VARIABLES
# -------------------------
ENV API_BASE_URL=http://localhost:8000

# -------------------------
# EXPOSE PORT
# -------------------------
EXPOSE 8000

# -------------------------
# START SERVER
# -------------------------
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]