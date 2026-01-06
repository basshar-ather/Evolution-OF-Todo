Phase V - DigitalOcean Kubernetes (DOKS)
========================================

This document contains steps and manifests to deploy the Evolution of Todo backend to DigitalOcean Kubernetes (DOKS).

Overview
--------
- The repo contains a Dockerfile at `phases/phase-4/backend/Dockerfile` used to build the backend image.
- Kubernetes manifests for DOKS are provided under `phases/phase-5/k8s/` as templates. Secrets and API keys are expected to be provided via Kubernetes Secrets or the DOKS UI.

Preconditions
-------------
- A DigitalOcean account and a Kubernetes cluster (DOKS).
- `doctl` CLI installed and authenticated, and `kubectl` configured for the DOKS cluster.
- (Optional) A container registry (Docker Hub or DigitalOcean Container Registry) to push the image.

Steps
-----
1. Build and push the image to a registry accessible by the DOKS cluster.

```powershell
# build locally
docker build -t <registry>/evo-todo-backend:latest -f phases/phase-4/backend/Dockerfile phases/phase-1/backend
# push
docker push <registry>/evo-todo-backend:latest
```

2. Create Kubernetes Secrets for environment variables and API keys.

```powershell
kubectl create secret generic evo-todo-secrets --from-literal=AI_API_KEY="<your_key>" --from-literal=SECRET_KEY="<secret>"
```

3. Apply manifests in `phases/phase-5/k8s/` (templates provided):

```powershell
kubectl apply -f phases/phase-5/k8s/deployment.yaml
kubectl apply -f phases/phase-5/k8s/service.yaml
kubectl apply -f phases/phase-5/k8s/ingress.yaml
```

Notes
-----
- For production, prefer a managed database (Postgres) instead of SQLite. The provided manifests use a PVC for SQLite as a minimal working example.
- Configure `ingress` and DNS records to expose the service externally and enable TLS with cert-manager.

