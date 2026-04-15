FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y iptables net-tools tcpdump && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p logs models/checkpoints data/processed

EXPOSE 8080

CMD ["python", "src/dashboard/app_complete.py"]
