# DevOps Practice App — Task Tracker API

A deliberately tiny FastAPI CRUD app. The app is not the point — it's the
payload for practicing a full DevOps pipeline: containerize → CI → deploy
to Kubernetes via GitOps → monitor → break things → recover.

No AWS account required anywhere in this flow.

## 0. Prerequisites

- Docker Desktop
- Python 3.12+
- kubectl
- [kind](https://kind.sigs.k8s.io/) or [minikube](https://minikube.sigs.k8s.io/) (local Kubernetes)
- A GitHub account (you already have this) + a new repo to push this into
- Helm (for the monitoring step later)
- Argo CD CLI (for the GitOps step later)

## 1. Run it locally (no Docker)

```bash
cd app
pip install -r requirements-dev.txt
uvicorn main:app --reload
# visit http://localhost:8000/docs for interactive Swagger UI
```

Run tests:

```bash
pytest tests -v
```

## 2. Run it in Docker

```bash
docker compose up --build
curl http://localhost:8000/health
```

## 3. Push to your own GitHub repo

```bash
git init
git add .
git commit -m "initial commit: task tracker api"
git branch -M main
git remote add origin https://github.com/<YOUR_GH_USERNAME>/<YOUR_REPO>.git
git push -u origin main
```

Pushing to `main` will trigger `.github/workflows/ci.yml`, which:
1. Runs pytest
2. Builds the Docker image
3. Scans it with Trivy
4. Pushes it to `ghcr.io/<YOUR_GH_USERNAME>/<YOUR_REPO>`

Check the **Actions** tab on GitHub to watch it run. Once it's pushed an
image, update `k8s/deployment.yaml`'s `image:` field with your actual
GHCR path.

> By default your GHCR package is private. Either make it public
> (package settings → Change visibility) or create a `ghcr` imagePullSecret
> in your cluster — public is simpler for local practice.

## 4. Spin up a local cluster and deploy

```bash
kind create cluster --name devops-practice
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

kubectl get pods
kubectl port-forward svc/task-api 8000:80
curl http://localhost:8000/health
```

## 5. Add GitOps with Argo CD (next rep)

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

kubectl port-forward svc/argocd-server -n argocd 8080:443
# get the initial admin password:
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

Point an Argo CD Application at the `k8s/` folder in your repo, set it to
auto-sync, then practice: change the replica count or image tag, push,
and watch Argo CD reconcile it automatically. Then practice a rollback
(`argocd app rollback` or `kubectl rollout undo`).

## 6. Add monitoring (next rep)

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
```

Port-forward Grafana, build one dashboard showing pod restarts and
request latency for `task-api`.

## 7. Break things on purpose

- `kubectl delete pod <pod-name>` — watch it get rescheduled, check Grafana
- Push a commit that fails a test — watch CI fail, read the logs
- Push a broken image tag to `deployment.yaml` — watch Argo CD sync a
  crashing pod, then roll back
- `kubectl scale deployment task-api --replicas=0` — simulate an outage,
  practice explaining MTTR while you bring it back

## What each folder is

| Path | Purpose |
|---|---|
| `app/` | The FastAPI application + tests |
| `Dockerfile` | Container build |
| `docker-compose.yml` | Local run without Kubernetes |
| `.github/workflows/ci.yml` | Test → build → scan → push pipeline |
| `k8s/` | Kubernetes manifests (Deployment, Service, ConfigMap) |
