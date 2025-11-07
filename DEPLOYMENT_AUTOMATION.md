# TigerEx Deployment Automation Guide

## 🚀 Overview

This comprehensive deployment automation guide covers the complete infrastructure setup, configuration, and deployment procedures for the TigerEx cryptocurrency exchange platform across all environments.

## 📋 Prerequisites

### System Requirements

- **Minimum**: 16 CPU cores, 64GB RAM, 1TB SSD storage
- **Recommended**: 32 CPU cores, 128GB RAM, 2TB NVMe storage
- **Operating System**: Ubuntu 22.04 LTS or RHEL 9
- **Network**: 10Gbps connectivity, DDoS protection
- **Security**: Hardware Security Module (HSM), dedicated VPN

### Software Dependencies

```bash
# Core Dependencies
- Docker Engine 24.0+
- Docker Compose 2.20+
- Kubernetes 1.28+
- Helm 3.13+
- Terraform 1.6+
- Ansible 2.15+
- GitHub CLI 2.0+
- kubectl 1.28+

# Development Tools
- Node.js 20.x
- Python 3.11+
- Go 1.21+
- Rust 1.75+
```

## 🏗️ Infrastructure Setup

### 1. Cloud Provider Configuration

#### AWS Setup

```bash
# Configure AWS CLI
aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
aws configure set region $AWS_REGION

# Create S3 buckets for storage
aws s3api create-bucket --bucket tigerex-production --region us-east-1
aws s3api create-bucket --bucket tigerex-backups --region us-east-1
aws s3api create-bucket --bucket tigerex-logs --region us-east-1

# Set up VPC and networking
terraform apply -target=aws_vpc.main
terraform apply -target=aws_subnet.public
terraform apply -target=aws_subnet.private
terraform apply -target=aws_internet_gateway.main
terraform apply -target=aws_route_table.public
terraform apply -target=aws_route_table.private
```

#### Kubernetes Cluster Setup

```bash
# Create EKS cluster
eksctl create cluster \
  --name tigerex-prod \
  --version 1.28 \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type m5.2xlarge \
  --nodes 6 \
  --nodes-min 3 \
  --nodes-max 12 \
  --managed

# Configure kubectl
aws eks update-kubeconfig --region us-east-1 --name tigerex-prod

# Install essential addons
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add cert-manager https://charts.jetstack.io
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace

helm install cert-manager cert-manager/cert-manager \
  --namespace cert-manager --create-namespace \
  --set installCRDs=true
```

### 2. Database Configuration

#### PostgreSQL Cluster Setup

```bash
# Deploy PostgreSQL Operator
kubectl create namespace postgres-operator
helm install postgres-operator \
  https://github.com/zalando/postgres-operator/releases/download/v1.10.0/postgres-operator-1.10.0.tgz \
  --namespace postgres-operator

# Create PostgreSQL cluster
cat <<EOF | kubectl apply -f -
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: tigerex-postgres-cluster
  namespace: postgres-operator
spec:
  instances: 3
  primaryUpdateStrategy: unsupervised

  postgresql:
    parameters:
      max_connections: "500"
      shared_buffers: "4GB"
      effective_cache_size: "12GB"
      work_mem: "256MB"
      maintenance_work_mem: "1GB"

  bootstrap:
    initdb:
      database: tigerex_prod
      owner: tigerex
      secret:
        name: postgres-credentials

  storage:
    size: 500Gi
    storageClass: io2
    pvcTemplate:
      accessModes:
        - ReadWriteOnce
      resources:
        requests:
          storage: 500Gi

  monitoring:
    enabled: true
EOF
```

#### Redis Cluster Setup

```bash
# Deploy Redis Operator
kubectl create namespace redis-operator
helm repo add ot-helm https://ot-container-kit.github.io/helm-charts
helm install redis-operator ot-helm/redis-operator \
  --namespace redis-operator

# Create Redis cluster
cat <<EOF | kubectl apply -f -
apiVersion: redis.redis.opstreelabs.in/v1beta1
kind: RedisCluster
metadata:
  name: tigerex-redis-cluster
  namespace: redis-operator
spec:
  clusterSize: 6
  clusterVersion: v7.0.12
  persistenceEnabled: true
  redisExporter:
    enabled: true
    image: oliver006/redis_exporter:latest
  storage:
    volumeClaimTemplate:
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 100Gi
        storageClassName: io2
EOF
```

## 🔧 Application Deployment

### 1. Environment Configuration

#### Production Environment Variables

```bash
# Create production secrets
kubectl create secret generic tigerex-secrets \
  --from-literal=DATABASE_URL="postgresql://tigerex:${DB_PASSWORD}@tigerex-postgres-cluster-rw:5432/tigerex_prod" \
  --from-literal=JWT_SECRET_KEY="${JWT_SECRET_KEY}" \
  --from-literal=ENCRYPTION_KEY="${ENCRYPTION_KEY}" \
  --from-literal=REDIS_CLUSTER_PASSWORD="${REDIS_PASSWORD}" \
  --from-literal=BINANCE_API_KEY="${BINANCE_API_KEY}" \
  --from-literal=BINANCE_API_SECRET="${BINANCE_API_SECRET}" \
  --from-literal=OKX_API_KEY="${OKX_API_KEY}" \
  --from-literal=OKX_API_SECRET="${OKX_API_SECRET}" \
  --from-literal=OKX_PASSPHRASE="${OKX_PASSPHRASE}" \
  --namespace=tigerex-production

# Create ConfigMaps
kubectl create configmap tigerex-config \
  --from-literal=NODE_ENV="production" \
  --from-literal=LOG_LEVEL="info" \
  --from-literal=API_RATE_LIMIT="1000" \
  --from-literal=ENABLE_METRICS="true" \
  --from-literal=ENABLE_TRACING="true" \
  --namespace=tigerex-production
```

### 2. Microservices Deployment

#### API Gateway

```yaml
# api-gateway-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: tigerex-production
spec:
  replicas: 4
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: tigerex/api-gateway:4.0.0
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: tigerex-secrets
              key: DATABASE_URL
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: tigerex-secrets
              key: JWT_SECRET_KEY
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway-service
  namespace: tigerex-production
spec:
  selector:
    app: api-gateway
  ports:
  - port: 8080
    targetPort: 8080
  type: ClusterIP
```

#### Trading Engine

```yaml
# trading-engine-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trading-engine
  namespace: tigerex-production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: trading-engine
  template:
    metadata:
      labels:
        app: trading-engine
    spec:
      containers:
      - name: trading-engine
        image: tigerex/trading-engine:4.0.0
        ports:
        - containerPort: 8002
        - containerPort: 8003  # WebSocket
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: tigerex-secrets
              key: DATABASE_URL
        - name: REDIS_CLUSTER_PASSWORD
          valueFrom:
            secretKeyRef:
              name: tigerex-secrets
              key: REDIS_CLUSTER_PASSWORD
        resources:
          requests:
            memory: "16Gi"
            cpu: "8"
          limits:
            memory: "32Gi"
            cpu: "16"
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
```

### 3. Frontend Applications

#### Web Application

```yaml
# web-app-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: tigerex-production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web-app
        image: tigerex/web-app:4.0.0
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "https://api.tigerex.com"
        - name: NEXT_PUBLIC_WS_URL
          value: "wss://api.tigerex.com"
        resources:
          requests:
            memory: "1Gi"
            cpu: "0.5"
          limits:
            memory: "2Gi"
            cpu: "1"
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-app-ingress
  namespace: tigerex-production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - tigerex.com
    - www.tigerex.com
    secretName: tigerex-tls
  rules:
  - host: tigerex.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-app-service
            port:
              number: 3000
```

## 📊 Monitoring & Observability

### 1. Prometheus Setup

```yaml
# prometheus-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:v2.45.0
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: prometheus-config
          mountPath: /etc/prometheus
        - name: prometheus-storage
          mountPath: /prometheus
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
      volumes:
      - name: prometheus-config
        configMap:
          name: prometheus-config
      - name: prometheus-storage
        persistentVolumeClaim:
          claimName: prometheus-pvc
```

### 2. Grafana Dashboard

```yaml
# grafana-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:10.2.0
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: grafana-secrets
              key: admin-password
        - name: GF_INSTALL_PLUGINS
          value: "grafana-piechart-panel,grafana-worldmap-panel"
        volumeMounts:
        - name: grafana-storage
          mountPath: /var/lib/grafana
        - name: grafana-config
          mountPath: /etc/grafana/provisioning
        resources:
          requests:
            memory: "1Gi"
            cpu: "0.5"
          limits:
            memory: "2Gi"
            cpu: "1"
```

## 🔒 Security Implementation

### 1. Network Policies

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: tigerex-network-policy
  namespace: tigerex-production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8080
  - from:
    - podSelector:
        matchLabels:
          app: web-app
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

### 2. Pod Security Policies

```yaml
# pod-security-policy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: tigerex-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

## 🚀 CI/CD Pipeline

### 1. GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy TigerEx

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: tigerex

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm test
    
    - name: Run security audit
      run: npm audit --audit-level moderate
    
    - name: Run ESLint
      run: npm run lint
    
    - name: Run TypeScript check
      run: npm run type-check

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    strategy:
      matrix:
        service: [api-gateway, trading-engine, wallet-service, web-app, admin-dashboard]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        file: ./${{ matrix.service }}/Dockerfile
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Update kubeconfig
      run: aws eks update-kubeconfig --region us-east-1 --name tigerex-prod
    
    - name: Deploy to Kubernetes
      run: |
        helm upgrade --install tigerex ./helm/tigerex \
          --namespace tigerex-production \
          --create-namespace \
          --set image.tag=${{ github.sha }} \
          --set ingress.host=tigerex.com \
          --values ./helm/tigerex/values-production.yaml
    
    - name: Verify deployment
      run: |
        kubectl rollout status deployment/api-gateway -n tigerex-production
        kubectl rollout status deployment/trading-engine -n tigerex-production
        kubectl rollout status deployment/web-app -n tigerex-production
```

### 2. Helm Chart Configuration

```yaml
# helm/tigerex/values-production.yaml
global:
  environment: production
  imageRegistry: ghcr.io/meghlabd275-byte
  imageTag: latest

api-gateway:
  replicaCount: 4
  image:
    repository: tigerex/api-gateway
  resources:
    requests:
      memory: "2Gi"
      cpu: "1"
    limits:
      memory: "4Gi"
      cpu: "2"
  autoscaling:
    enabled: true
    minReplicas: 4
    maxReplicas: 12
    targetCPUUtilizationPercentage: 70

trading-engine:
  replicaCount: 2
  image:
    repository: tigerex/trading-engine
  resources:
    requests:
      memory: "16Gi"
      cpu: "8"
    limits:
      memory: "32Gi"
      cpu: "16"

web-app:
  replicaCount: 3
  image:
    repository: tigerex/web-app
  ingress:
    enabled: true
    hosts:
      - host: tigerex.com
        paths:
          - path: /
            pathType: Prefix
    tls:
      - secretName: tigerex-tls
        hosts:
          - tigerex.com

postgresql:
  enabled: true
  auth:
    postgresPassword: ${POSTGRES_PASSWORD}
    database: tigerex_prod
  primary:
    persistence:
      enabled: true
      size: 500Gi
      storageClass: io2
  readReplicas:
    replicaCount: 2
    persistence:
      enabled: true
      size: 250Gi

redis:
  enabled: true
  auth:
    enabled: true
    password: ${REDIS_PASSWORD}
  master:
    persistence:
      enabled: true
      size: 100Gi
  replica:
    replicaCount: 2
    persistence:
      enabled: true
      size: 50Gi
```

## 🔧 Maintenance Operations

### 1. Backup Procedures

```bash
#!/bin/bash
# backup-script.sh

# Database backup
kubectl exec -n postgres-operator tigerex-postgres-cluster-1 -- pg_dump \
  -U tigerex -d tigerex_prod | gzip > backup-$(date +%Y%m%d-%H%M%S).sql.gz

# Upload to S3
aws s3 cp backup-$(date +%Y%m%d-%H%M%S).sql.gz \
  s3://tigerex-backups/database/$(date +%Y)/$(date +%m)/

# Redis backup
kubectl exec -n redis-operator tigerex-redis-cluster-master-0 -- \
  redis-cli BGSAVE

# Configuration backup
kubectl get all -n tigerex-production -o yaml > config-backup-$(date +%Y%m%d-%H%M%S).yaml

# Clean up old backups (keep 30 days)
aws s3 ls s3://tigerex-backups/database/ | \
  while read -r line; do
    createDate=$(echo $line | awk '{print $1" "$2}')
    createDate=$(date -d "$createDate" +%s)
    olderThan=$(date -d "30 days ago" +%s)
    if [[ $createDate -lt $olderThan ]]; then
      fileName=$(echo $line | awk '{print $4}')
      aws s3 rm s3://tigerex-backups/database/$fileName
    fi
  done
```

### 2. Scaling Operations

```bash
#!/bin/bash
# scaling-script.sh

# Scale up during high traffic
kubectl scale deployment api-gateway --replicas=8 -n tigerex-production
kubectl scale deployment trading-engine --replicas=4 -n tigerex-production
kubectl scale deployment web-app --replicas=6 -n tigerex-production

# Enable autoscaling
kubectl autoscale deployment api-gateway \
  --cpu-percent=70 --min=4 --max=16 -n tigerex-production

kubectl autoscale deployment trading-engine \
  --cpu-percent=80 --min=2 --max=8 -n tigerex-production

kubectl autoscale deployment web-app \
  --cpu-percent=70 --min=3 --max=12 -n tigerex-production

# Scale down during low traffic
kubectl scale deployment api-gateway --replicas=4 -n tigerex-production
kubectl scale deployment trading-engine --replicas=2 -n tigerex-production
kubectl scale deployment web-app --replicas=3 -n tigerex-production
```

### 3. Update Procedures

```bash
#!/bin/bash
# update-script.sh

# Update application with zero downtime
helm upgrade tigerex ./helm/tigerex \
  --namespace tigerex-production \
  --set image.tag=$NEW_VERSION \
  --values ./helm/tigerex/values-production.yaml \
  --wait \
  --timeout=10m

# Verify deployment
kubectl rollout status deployment/api-gateway -n tigerex-production
kubectl rollout status deployment/trading-engine -n tigerex-production
kubectl rollout status deployment/web-app -n tigerex-production

# Run health checks
curl -f https://api.tigerex.com/health
curl -f https://tigerex.com/api/health

# Monitor for issues
kubectl logs -f deployment/api-gateway -n tigerex-production --tail=100
```

## 📈 Performance Optimization

### 1. Database Optimization

```sql
-- PostgreSQL performance tuning
ALTER SYSTEM SET shared_buffers = '8GB';
ALTER SYSTEM SET effective_cache_size = '24GB';
ALTER SYSTEM SET work_mem = '512MB';
ALTER SYSTEM SET maintenance_work_mem = '2GB';
ALTER SYSTEM SET max_connections = '1000';
ALTER SYSTEM SET checkpoint_completion_target = '0.9';
ALTER SYSTEM SET wal_buffers = '64MB';
ALTER SYSTEM SET default_statistics_target = '100';

-- Create indexes for performance
CREATE INDEX CONCURRENTLY idx_trades_user_id ON trades(user_id);
CREATE INDEX CONCURRENTLY idx_trades_created_at ON trades(created_at);
CREATE INDEX CONCURRENTLY idx_orders_status ON orders(status);
CREATE INDEX CONCURRENTLY idx_orders_trading_pair ON orders(trading_pair);

-- Update statistics
ANALYZE trades;
ANALYZE orders;
ANALYZE users;
```

### 2. Redis Optimization

```bash
# Redis configuration optimization
redis-cli CONFIG SET maxmemory 16gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
redis-cli CONFIG SET save "900 1 300 10 60 10000"
redis-cli CONFIG SET tcp-keepalive 60
redis-cli CONFIG SET timeout 0
redis-cli CONFIG SET tcp-backlog 511
```

## 🔍 Troubleshooting

### Common Issues and Solutions

1. **High Memory Usage**
   ```bash
   # Check memory usage
   kubectl top pods -n tigerex-production
   
   # Check pod resources
   kubectl describe pod <pod-name> -n tigerex-production
   
   # Increase memory limits
   kubectl patch deployment api-gateway -p '{"spec":{"template":{"spec":{"containers":[{"name":"api-gateway","resources":{"limits":{"memory":"8Gi"}}}]}}}}'
   ```

2. **Database Connection Issues**
   ```bash
   # Check database connections
   kubectl exec -it tigerex-postgres-cluster-1 -n postgres-operator -- psql -U tigerex -c "SELECT count(*) FROM pg_stat_activity;"
   
   # Check connection pool
   kubectl logs deployment/api-gateway -n tigerex-production | grep -i "connection"
   ```

3. **API Response Time Issues**
   ```bash
   # Check API latency
   curl -w "@curl-format.txt" -o /dev/null -s https://api.tigerex.com/health
   
   # Check resource utilization
   kubectl top pods -n tigerex-production
   ```

## 📊 Monitoring Dashboards

### Key Metrics to Monitor

1. **Application Metrics**
   - Request rate and latency
   - Error rate and status codes
   - Active connections and sessions
   - CPU and memory usage

2. **Business Metrics**
   - Trading volume and transactions
   - User registrations and logins
   - Order book depth and spread
   - Withdrawal and deposit amounts

3. **Infrastructure Metrics**
   - Database query performance
   - Redis memory usage
   - Network throughput
   - Storage utilization

## 🔔 Alerting Configuration

### Prometheus Alert Rules

```yaml
# alert-rules.yaml
groups:
- name: tigerex-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"

  - alert: HighLatency
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High latency detected"
      description: "95th percentile latency is {{ $value }} seconds"

  - alert: DatabaseConnectionsHigh
    expr: pg_stat_activity_count > 400
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High database connections"
      description: "Database has {{ $value }} active connections"
```

## 📚 Documentation & Training

### Documentation Requirements

1. **Technical Documentation**
   - Architecture diagrams
   - API documentation
   - Configuration guides
   - Troubleshooting procedures

2. **Operational Documentation**
   - Runbooks for common issues
   - Incident response procedures
   - Backup and recovery procedures
   - Maintenance schedules

3. **User Documentation**
   - Feature guides
   - API usage examples
   - Best practices
   - FAQ and support

---

*This deployment automation guide ensures consistent, reliable, and secure deployments of the TigerEx platform across all environments.*