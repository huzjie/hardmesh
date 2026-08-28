# 部署指南

## Docker

```bash
docker compose up --build
```

## Kubernetes

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

## Helm

```bash
helm install hardmesh ./helm/hardmesh
```
