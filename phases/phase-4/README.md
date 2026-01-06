Phase IV - Local Kubernetes Deployment
======================================

This phase contains a Dockerfile and Kubernetes manifests to deploy the Phase I/II/III backend locally on Minikube.

Overview
--------
- Dockerfile builds the FastAPI backend image.
- Kubernetes manifests create a Deployment, Service, and PersistentVolumeClaim for SQLite persistence.

Build and deploy on Minikube (recommended)
-----------------------------------------
1. Start Minikube:

```powershell
minikube start
```

2. Build the image inside Minikube so it is available to the cluster:

```powershell
minikube image build -t evo-todo-backend:latest phases/phase-1/backend -f phases/phase-4/backend/Dockerfile
```

3. Apply Kubernetes manifests:

```powershell
kubectl apply -f phases/phase-4/k8s/pvc.yaml
kubectl apply -f phases/phase-4/k8s/deployment.yaml
kubectl apply -f phases/phase-4/k8s/service.yaml
```

4. Verify pods and service:

```powershell
kubectl get pods
kubectl get svc
```

5. Port-forward the service to test locally:

```powershell
kubectl port-forward svc/evo-todo-service 8000:8000
# then visit http://127.0.0.1:8000/docs
```

Build and deploy with Docker (alternative)
-----------------------------------------
1. Build the image using Docker:

```powershell
docker build -t evo-todo-backend:latest -f phases/phase-4/backend/Dockerfile phases/phase-1/backend
```

2. Load image into Minikube (if needed):

```powershell
minikube image load evo-todo-backend:latest
```

3. Apply manifests (same as above).

Notes
-----
- Manifests mount a PVC at `/data` and the application uses `sqlite:////data/database.db` as the DB path.
- This deployment follows the Phase I spec exactly; no extra features are added.

