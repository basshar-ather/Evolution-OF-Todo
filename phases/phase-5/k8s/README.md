Phase V Kubernetes Manifests
===========================

This folder contains template manifests for deploying the backend to DigitalOcean Kubernetes (DOKS).

Files:
- `deployment.yaml` - Deployment for the backend; edit the `image` value to point to your registry.
- `service.yaml` - ClusterIP service exposing port 80 -> container 8000.
- `ingress.yaml` - Ingress template; replace `<your.domain.example>` with your domain.
- `pvc.yaml` - PersistentVolumeClaim for SQLite storage (example `do-block-storage` storageClass).
- `secret.yaml` - Secret template for runtime secrets (use `stringData` for easy editing).

Quick apply example (after editing values):

```powershell
kubectl apply -f phases/phase-5/k8s/secret.yaml
kubectl apply -f phases/phase-5/k8s/pvc.yaml
kubectl apply -f phases/phase-5/k8s/deployment.yaml
kubectl apply -f phases/phase-5/k8s/service.yaml
kubectl apply -f phases/phase-5/k8s/ingress.yaml
```

Notes:
- Replace the image placeholder with an image accessible to your cluster.
- For production use Postgres or a managed DB instead of SQLite. A Postgres template is provided in `phases/phase-5/k8s/postgres.yaml`.
- You can run the stack locally with `docker-compose.yml` in the repo root which brings up Postgres + backend (see `phases/phase-4/backend/README.md`).
