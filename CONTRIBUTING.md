# Contributing

## How to build the Dockerfile locally
```
docker build -t flask-stores-api .
```

## How to run the Dockerfile locally

```
docker run -dp 5000:5000 -w /app -v "$(pwd):/app" flask-stores-api sh -c "flask run"
```