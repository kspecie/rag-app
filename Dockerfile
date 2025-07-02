FROM vault.habana.ai/gaudi-docker/1.21.1/rhel9.2/habanalabs/pytorch-installer-2.6.0:latest

WORKDIR /app
COPY requirements.txt .
RUN pip install --no cache--dir -r requirements.txt
COPY app/ ./app
COPY data/ ./data
EXPOSE 8000


CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]