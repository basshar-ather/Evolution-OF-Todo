# Build and deploy script for Minikube
# Run from repo root

Set-StrictMode -Version Latest

$root = Resolve-Path .
Push-Location $root

Write-Host "Building image inside Minikube..."
minikube image build -t evo-todo-backend:latest phases/phase-1/backend -f phases/phase-4/backend/Dockerfile

Write-Host "Applying manifests..."
kubectl apply -f phases/phase-4/k8s/pvc.yaml
kubectl apply -f phases/phase-4/k8s/configmap.yaml
kubectl apply -f phases/phase-4/k8s/deployment.yaml
kubectl apply -f phases/phase-4/k8s/service.yaml
kubectl apply -f phases/phase-4/k8s/ingress.yaml

Write-Host "Done. Use 'kubectl get pods' and 'kubectl port-forward svc/evo-todo-service 8000:8000' to access the app."
Pop-Location
