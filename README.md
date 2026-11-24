# github_actions_multi_environment_deployment
==============================================

github-actions-multi-env-deployment/
│
├── app/
│   ├── app.py
│   └── requirements.txt
│
├── Dockerfile
│
└── .github/
    └── workflows/
        └── multi-env-deploy.yml


============================================================
++++++++++++++++app.py+++++++++++++++

import os

app = Flask(_name_)

ENVIRONMENT = os.getenv("APP_ENV", "development")

@app.route("/")
def home():
    return jsonify({
        "application": "GitHub Actions Multi Environment",
        "environment": ENVIRONMENT,
        "status": "Running successfully"
    })

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "environment": ENVIRONMENT
    })

if _name_ == "_main_":
    app.run(host="0.0.0.0", port=5000)


============================================================
++++++++requirements.txt+++++++++++

Flask==3.1.0


========================================================
++++++++++Dockerfile++++++++++++

FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

EXPOSE 5000

CMD ["python", "app.py"]


=========================================================
++++++++++yaml+++++++++++++++

name: Multi Environment Deployment

on:
  push:
    branches:
      - develop
      - qa
      - main

  workflow_dispatch:

permissions:
  contents: read
  packages: write

env:
  IMAGE_NAME: ghcr.io/${{ github.repository }}

jobs:

  # -------------------------
  # 1. BUILD AND PUSH
  # -------------------------

  build:
    name: Build Docker Image
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and Push Docker Image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ env.IMAGE_NAME }}:${{ github.sha }}

  # -------------------------
  # 2. DEVELOPMENT DEPLOYMENT
  # -------------------------

  deploy-dev:
    name: Deploy DEV
    needs: build
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    environment: development

    steps:
      - name: Deploy to Development
        uses: appleboy/ssh-action@v1.2.2
        env:
          IMAGE: ${{ env.IMAGE_NAME }}:${{ github.sha }}
          APP_ENV: development
          CONTAINER_NAME: dev-app
          HOST_PORT: 8081
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          envs: IMAGE,APP_ENV,CONTAINER_NAME,HOST_PORT
          script: |
            docker pull $IMAGE
            docker rm -f $CONTAINER_NAME || true
            docker run -d \
              --name $CONTAINER_NAME \
              --restart unless-stopped \
              -p $HOST_PORT:5000 \
              -e APP_ENV=$APP_ENV \
              $IMAGE

            sleep 5
            curl -f http://localhost:$HOST_PORT/health

  # -------------------------
  # 3. QA DEPLOYMENT
  # -------------------------

  deploy-qa:
    name: Deploy QA
    needs: build
    if: github.ref == 'refs/heads/qa'
    runs-on: ubuntu-latest
    environment: qa

    steps:
      - name: Deploy to QA
        uses: appleboy/ssh-action@v1.2.2
        env:
          IMAGE: ${{ env.IMAGE_NAME }}:${{ github.sha }}
          APP_ENV: qa
          CONTAINER_NAME: qa-app
          HOST_PORT: 8082
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          envs: IMAGE,APP_ENV,CONTAINER_NAME,HOST_PORT
          script: |
            docker pull $IMAGE
            docker rm -f $CONTAINER_NAME || true
            docker run -d \
              --name $CONTAINER_NAME \
              --restart unless-stopped \
              -p $HOST_PORT:5000 \
              -e APP_ENV=$APP_ENV \
              $IMAGE

            sleep 5
            curl -f http://localhost:$HOST_PORT/health

  # -------------------------
  # 4. PRODUCTION DEPLOYMENT
  # -------------------------

  deploy-prod:
    name: Deploy PROD
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production

    steps:
      - name: Deploy to Production
        uses: appleboy/ssh-action@v1.2.2
        env:
          IMAGE: ${{ env.IMAGE_NAME }}:${{ github.sha }}
          APP_ENV: production
          CONTAINER_NAME: prod-app
          HOST_PORT: 8083
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          envs: IMAGE,APP_ENV,CONTAINER_NAME,HOST_PORT
          script: |
            docker pull $IMAGE
            docker rm -f $CONTAINER_NAME || true
            docker run -d \
              --name $CONTAINER_NAME \
              --restart unless-stopped \
              -p $HOST_PORT:5000 \
              -e APP_ENV=$APP_ENV \
              $IMAGE

            sleep 5
            curl -f http://localhost:$HOST_PORT/health


