FROM pyd4vinci/scrapling:latest

WORKDIR /app

# Install FastAPI and uvicorn on top of the existing Scrapling image
RUN pip install fastapi uvicorn --break-system-packages

# Copy our API server
COPY api.py .

EXPOSE 8000

CMD ["python", "api.py"]