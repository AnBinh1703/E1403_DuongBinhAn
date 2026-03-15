FROM python:3.11-slim

WORKDIR /workspace

COPY requirements.txt ./
COPY notebook/requirements.txt ./notebook/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8888

CMD ["bash", "-lc", "jupyter lab --ip=0.0.0.0 --port=8888 --allow-root --no-browser"]
