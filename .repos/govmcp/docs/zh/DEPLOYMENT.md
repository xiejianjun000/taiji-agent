# 政务MCP协议 部署指南

本文档详细描述了 govmcp 项目的各种部署方案和配置方法。

## 目录

- [环境要求](#环境要求)
- [安装部署](#安装部署)
- [Docker部署](#docker部署)
- [Kubernetes部署](#kubernetes部署)
- [系统配置](#系统配置)
- [安全配置](#安全配置)
- [监控与日志](#监控与日志)
- [备份与恢复](#备份与恢复)
- [高可用部署](#高可用部署)
- [故障排除](#故障排除)

---

## 环境要求

### 硬件要求

| 环境类型 | CPU | 内存 | 磁盘 | 网络 |
|---------|-----|------|------|------|
| 开发测试 | 2核 | 4GB | 20GB | 100Mbps |
| 小规模生产 | 4核 | 8GB | 50GB | 500Mbps |
| 中等规模生产 | 8核 | 16GB | 100GB | 1Gbps |
| 大规模生产 | 16核+ | 32GB+ | 200GB+ | 10Gbps |

### 软件要求

- **操作系统**：Ubuntu 20.04+ / CentOS 7+ / 麒麟V10 / 统信UOS
- **Python**：3.10+
- **数据库**：MySQL 8.0+ / PostgreSQL 13+ / 达梦8+
- **缓存**：Redis 6.0+（可选）
- **消息队列**：RabbitMQ 3.8+（可选，用于异步任务）

### 国产化环境支持

| 组件 | 支持版本 |
|-----|---------|
| 操作系统 | 麒麟V10、统信UOS、普华OS |
| CPU架构 | x86_64、ARM64（鲲鹏、飞腾） |
| 数据库 | 达梦8、人大金仓V8、神通国产 |
| 中间件 | 东方通TongWeb、金蝶Apusic |

---

## 安装部署

### 方式一：pip安装

```bash
# 创建虚拟环境
python3 -m venv govmcp-env
source govmcp-env/bin/activate

# 安装最新版本
pip install govmcp

# 安装指定版本
pip install govmcp==1.0.0

# 安装开发版本
pip install govmcp --pre
```

### 方式二：源码安装

```bash
# 克隆代码
git clone https://github.com/govmcp/govmcp.git
cd govmcp

# 安装依赖
pip install -e .

# 或使用poetry安装
poetry install
```

### 方式三：离线安装

```bash
# 在有网络的环境下载依赖
pip download -r requirements.txt -d ./packages

# 传输到目标机器
scp -r ./packages user@target:/tmp/

# 在目标机器安装
pip install --no-index --find-links=/tmp/packages -r requirements.txt
```

---

## Docker部署

### 基础Docker部署

#### Dockerfile

```dockerfile
FROM python:3.10-slim

LABEL maintainer="govmcp@example.com"
LABEL description="政务MCP协议服务"

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 govmcp && chown -R govmcp:govmcp /app
USER govmcp

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "-m", "govmcp.server"]
```

#### 构建镜像

```bash
# 构建镜像
docker build -t govmcp:latest .

# 查看镜像
docker images govmcp
```

#### 运行容器

```bash
# 运行容器
docker run -d \
  --name govmcp-server \
  -p 8080:8080 \
  -v /data/govmcp:/data \
  -e GOVMCP_ENCRYPTION_ENABLED=true \
  -e GOVMCP_AUDIT_ENABLED=true \
  -e GOVMCP_LOG_LEVEL=INFO \
  --restart unless-stopped \
  govmcp:latest
```

### Docker Compose部署

#### docker-compose.yaml

```yaml
version: '3.8'

services:
  govmcp:
    image: govmcp:latest
    container_name: govmcp-server
    ports:
      - "8080:8080"
    volumes:
      - ./config:/app/config
      - ./data:/data
      - ./logs:/var/log/govmcp
    environment:
      - GOVMCP_SERVER_NAME=govmcp-prod
      - GOVMCP_ENCRYPTION_ENABLED=true
      - GOVMCP_AUDIT_ENABLED=true
      - GOVMCP_DB_TYPE=mysql
      - GOVMCP_DB_HOST=mysql
      - GOVMCP_DB_PORT=3306
      - GOVMCP_DB_NAME=govmcp
      - GOVMCP_DB_USER=govmcp
      - GOVMCP_DB_PASSWORD=${DB_PASSWORD}
      - GOVMCP_REDIS_HOST=redis
      - GOVMCP_REDIS_PORT=6379
      - GOVMCP_LOG_LEVEL=INFO
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped
    networks:
      - govmcp-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  mysql:
    image: mysql:8.0
    container_name: govmcp-mysql
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=govmcp
      - MYSQL_USER=govmcp
      - MYSQL_PASSWORD=${DB_PASSWORD}
    volumes:
      - mysql-data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "3306:3306"
    networks:
      - govmcp-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:6-alpine
    container_name: govmcp-redis
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"
    networks:
      - govmcp-network

networks:
  govmcp-network:
    driver: bridge

volumes:
  mysql-data:
  redis-data:
```

#### 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f govmcp

# 停止服务
docker-compose down
```

---

## Kubernetes部署

### Helm Chart部署

#### 添加Helm仓库

```bash
# 添加官方仓库
helm repo add govmcp https://charts.govmcp.org
helm repo update

# 搜索Chart
helm search repo govmcp
```

#### 安装Chart

```bash
# 创建命名空间
kubectl create namespace govmcp

# 安装
helm install govmcp govmcp/govmcp \
  --namespace govmcp \
  --set image.tag=v1.0.0 \
  --set encryption.enabled=true \
  --set audit.enabled=true \
  --set persistence.enabled=true \
  --set persistence.size=50Gi
```

### K8s资源清单部署

#### Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: govmcp
  labels:
    app: govmcp
```

#### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: govmcp-config
  namespace: govmcp
data:
  config.yaml: |
    server:
      name: govmcp
      port: 8080
    encryption:
      enabled: true
      algorithm: sm4
    audit:
      enabled: true
      retention_days: 180
    logging:
      level: INFO
      format: json
```

#### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: govmcp-server
  namespace: govmcp
  labels:
    app: govmcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: govmcp
  template:
    metadata:
      labels:
        app: govmcp
    spec:
      containers:
        - name: govmcp
          image: govmcp:latest
          ports:
            - containerPort: 8080
          env:
            - name: GOVMCP_CONFIG_PATH
              value: /app/config/config.yaml
            - name: GOVMCP_ENCRYPTION_ENABLED
              value: "true"
            - name: GOVMCP_AUDIT_ENABLED
              value: "true"
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
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
          volumeMounts:
            - name: config
              mountPath: /app/config
            - name: data
              mountPath: /data
      volumes:
        - name: config
          configMap:
            name: govmcp-config
        - name: data
          persistentVolumeClaim:
            claimName: govmcp-data
```

#### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: govmcp-service
  namespace: govmcp
spec:
  selector:
    app: govmcp
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
  type: ClusterIP
```

#### HPA自动扩缩容

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: govmcp-hpa
  namespace: govmcp
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: govmcp-server
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

#### 应用资源

```bash
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml
```

---

## 系统配置

### 配置文件结构

```
/etc/govmcp/
├── config.yaml           # 主配置文件
├── security.yaml         # 安全配置
├── database.yaml         # 数据库配置
├── logging.yaml          # 日志配置
└── plugins/              # 插件配置
    └── enabled/          # 启用的插件
```

### 主配置文件示例

```yaml
# config.yaml
server:
  name: govmcp-prod
  host: 0.0.0.0
  port: 8080
  workers: 4
  timeout: 300
  max_requests: 1000

encryption:
  enabled: true
  algorithm: sm4
  key_rotation_days: 90
  key_storage: env  # env/kms/hsm

audit:
  enabled: true
  log_path: /var/log/govmcp/audit.log
  retention_days: 180
  encrypt_logs: true
  log_format: json

database:
  type: mysql
  host: localhost
  port: 3306
  name: govmcp
  user: govmcp
  password: ${DB_PASSWORD}
  pool_size: 20
  pool_recycle: 3600

redis:
  host: localhost
  port: 6379
  password: ${REDIS_PASSWORD}
  db: 0
  max_connections: 50

tools:
  registry:
    enabled: true
    path: /var/lib/govmcp/tools
  builtin:
    enabled: true
    categories:
      - enterprise
      - personal
      - approval
      - security

logging:
  level: INFO
  format: json
  handlers:
    console:
      enabled: true
      level: INFO
    file:
      enabled: true
      level: DEBUG
      path: /var/log/govmcp/app.log
      max_bytes: 104857600
      backup_count: 10
    syslog:
      enabled: false
      facility: local0
```

### 环境变量

| 变量名 | 描述 | 默认值 |
|-------|------|--------|
| GOVMCP_CONFIG_PATH | 配置文件路径 | /etc/govmcp/config.yaml |
| GOVMCP_SERVER_NAME | 服务器名称 | govmcp |
| GOVMCP_PORT | 服务端口 | 8080 |
| GOVMCP_ENCRYPTION_ENABLED | 启用加密 | true |
| GOVMCP_AUDIT_ENABLED | 启用审计 | true |
| GOVMCP_DB_TYPE | 数据库类型 | mysql |
| GOVMCP_DB_HOST | 数据库地址 | localhost |
| GOVMCP_DB_PORT | 数据库端口 | 3306 |
| GOVMCP_DB_NAME | 数据库名 | govmcp |
| GOVMCP_DB_USER | 数据库用户 | govmcp |
| GOVMCP_DB_PASSWORD | 数据库密码 | - |
| GOVMCP_REDIS_HOST | Redis地址 | localhost |
| GOVMCP_REDIS_PORT | Redis端口 | 6379 |
| GOVMCP_REDIS_PASSWORD | Redis密码 | - |
| GOVMCP_LOG_LEVEL | 日志级别 | INFO |
| GOVMCP_SM4_KEY | SM4加密密钥 | - |

---

## 安全配置

### TLS配置

```yaml
# security.yaml
tls:
  enabled: true
  cert_file: /etc/govmcp/tls/server.crt
  key_file: /etc/govmcp/tls/server.key
  ca_file: /etc/govmcp/tls/ca.crt
  min_version: "1.2"
  cipher_suites:
    - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
    - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256

authentication:
  type: token
  token:
    secret: ${TOKEN_SECRET}
    expire_hours: 8
    refresh_enabled: true
    refresh_expire_hours: 72

access_control:
  ip_whitelist:
    - "10.0.0.0/8"
    - "172.16.0.0/12"
  rate_limit:
    enabled: true
    requests_per_minute: 100
    burst: 20
```

### 生成自签名证书

```bash
# 生成私钥
openssl genrsa -out server.key 2048

# 生成证书请求
openssl req -new -key server.key -out server.csr

# 自签名证书（测试用）
openssl x509 -req -in server.csr -signkey server.key -out server.crt

# 正式环境应使用CA签发的证书
```

---

## 监控与日志

### Prometheus监控

```yaml
# prometheus.yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'govmcp'
    static_configs:
      - targets: ['govmcp-service:8080']
    metrics_path: /metrics
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "GovMCP监控面板",
    "panels": [
      {
        "title": "请求QPS",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(govmcp_requests_total[5m])",
            "legendFormat": "QPS"
          }
        ]
      },
      {
        "title": "响应延迟P99",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, rate(govmcp_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P99"
          }
        ]
      },
      {
        "title": "错误率",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(govmcp_errors_total[5m]) / rate(govmcp_requests_total[5m])",
            "legendFormat": "错误率"
          }
        ]
      }
    ]
  }
}
```

### 日志收集

```yaml
# filebeat.yaml
filebeat.inputs:
  - type: log
    paths:
      - /var/log/govmcp/*.log
    json.keys_under_root: true
    fields:
      service: govmcp
      environment: production

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "govmcp-%{+yyyy.MM.dd}"
```

---

## 备份与恢复

### 数据库备份

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backup/govmcp
DB_NAME=govmcp
DB_USER=govmcp
DB_PASSWORD=${DB_PASSWORD}

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 备份数据库
mysqldump -u${DB_USER} -p${DB_PASSWORD} ${DB_NAME} | gzip > ${BACKUP_DIR}/govmcp_${DATE}.sql.gz

# 保留最近30天的备份
find ${BACKUP_DIR} -name "govmcp_*.sql.gz" -mtime +30 -delete

# 上传到对象存储（可选）
# ossutil cp ${BACKUP_DIR}/govmcp_${DATE}.sql.gz oss://bucket/govmcp-backup/
```

### 数据恢复

```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=/backup/govmcp/govmcp_20240101_120000.sql.gz
DB_NAME=govmcp
DB_USER=govmcp
DB_PASSWORD=${DB_PASSWORD}

# 停止服务
docker-compose stop govmcp

# 恢复数据
gunzip -c ${BACKUP_FILE} | mysql -u${DB_USER} -p${DB_PASSWORD} ${DB_NAME}

# 启动服务
docker-compose start govmcp
```

---

## 高可用部署

### 双机热备架构

```
                    ┌─────────────────┐
                    │   负载均衡器     │
                    │  (Nginx/HAProxy) │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
        │  GovMCP1  │  │  GovMCP2  │  │  GovMCP3  │
        │ (主节点)  │  │ (热备)    │  │ (热备)    │
        └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        ┌─────▼─────┐  ┌─────▼─────┐
        │   MySQL   │  │   Redis   │
        │  (主从)   │  │  (集群)   │
        └───────────┘  └───────────┘
```

### Keepalived配置

```bash
# /etc/keepalived/keepalived.conf
vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1234
    }
    virtual_ipaddress {
        10.0.0.100
    }
    track_script {
        chk_govmcp
    }
}

vrrp_script chk_govmcp {
    script "/usr/local/bin/check_govmcp.sh"
    interval 2
    weight 2
}
```

---

## 故障排除

### 常见问题

#### 1. 服务启动失败

```bash
# 检查日志
journalctl -u govmcp -n 100

# 检查端口占用
netstat -tlnp | grep 8080

# 检查配置文件
python -c "import yaml; yaml.safe_load(open('/etc/govmcp/config.yaml'))"
```

#### 2. 数据库连接失败

```bash
# 测试数据库连接
mysql -h localhost -u govmcp -p -e "SELECT 1"

# 检查连接数
mysql -e "SHOW PROCESSLIST;"
```

#### 3. 加密/解密失败

```bash
# 检查密钥配置
grep SM4_KEY /etc/govmcp/config.yaml

# 测试加密功能
python -c "
from govmcp.crypto import SM4
sm4 = SM4(key=b'32-byte-secret-key-for-sm4!!')
print(sm4.encrypt_str('test'))
"
```

#### 4. 审计链验证失败

```bash
# 检查审计日志
tail -f /var/log/govmcp/audit.log | jq

# 手动验证审计链
python -c "
from govmcp.models import AuditChain
chain = AuditChain.from_dict({'chain_id': 'test'})
print(chain.verify())
"
```

### 健康检查

```bash
# HTTP健康检查
curl -f http://localhost:8080/health

# 详细状态
curl http://localhost:8080/status

# 数据库连接
curl http://localhost:8080/health/db

# 加密模块
curl http://localhost:8080/health/crypto
```

---

## 相关链接

- [快速开始指南](./QUICKSTART.md)
- [高级指南](./ADVANCED.md)
- [API参考](./API.md)
- [安全指南](./SECURITY.md)
