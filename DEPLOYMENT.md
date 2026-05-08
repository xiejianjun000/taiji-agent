# OpenTaiji 生产级部署指南

## 概述

本文档提供 OpenTaiji 的生产级部署方案，包含 Docker、Kubernetes 和裸机部署三种方式。

## 系统要求

### 最低配置
- CPU: 2 核
- 内存: 4 GB
- 存储: 20 GB SSD
- 网络: 100 Mbps

### 推荐配置
- CPU: 4 核+
- 内存: 8 GB+
- 存储: 50 GB SSD
- 网络: 1 Gbps

## 快速开始

### 方式一：Docker Compose（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/xiejianjun000/open-taiji.git
cd open-taiji

# 2. 配置环境变量
cp .env.example .env.production
# 编辑 .env.production 填入实际值

# 3. 启动服务
docker-compose up -d

# 4. 验证部署
curl http://localhost:3000/health
```

### 方式二：Kubernetes

```bash
# 1. 创建命名空间
kubectl apply -f k8s/namespace.yaml

# 2. 创建 ConfigMap 和 Secret
kubectl apply -f k8s/configmap.yaml
kubectl create secret generic opentaiji-secrets \
  --from-literal=JWT_SECRET=your-secret \
  --from-literal=API_KEY=your-key \
  -n opentaiji

# 3. 部署应用
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml

# 4. 验证部署
kubectl get pods -n opentaiji
kubectl logs -f deployment/opentaiji -n opentaiji
```

### 方式三：裸机部署

```bash
# 1. 安装 Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 2. 安装依赖
npm ci --production

# 3. 构建应用
npm run build

# 4. 配置 systemd
sudo cp deploy/opentaiji.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable opentaiji
sudo systemctl start opentaiji
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| NODE_ENV | 运行环境 | production |
| PORT | 服务端口 | 3000 |
| LOG_LEVEL | 日志级别 | info |
| JWT_SECRET | JWT 签名密钥 | 必填 |
| REDIS_URL | Redis 连接地址 | redis://localhost:6379 |

### 配置文件

配置文件位于 `config/` 目录，支持 YAML 格式：

```yaml
# config/production.yml
app:
  name: OpenTaiji
  version: 1.1.0

logging:
  level: info
  format: json
  output: /var/log/opentaiji/app.log

security:
  jwt:
    expiresIn: 24h
    algorithm: HS256
  rateLimit:
    enabled: true
    requestsPerMinute: 1000

features:
  wfgy:
    enabled: true
    verificationLevel: strict
  actor:
    mailboxSize: 100
    supervisionStrategy: restart
```

## 监控与告警

### Prometheus 指标

访问 `http://localhost:9090` 查看 Prometheus 控制台。

主要指标：
- `opentaiji_requests_total`: 请求总数
- `opentaiji_request_duration_seconds`: 请求延迟
- `opentaiji_active_connections`: 活跃连接数
- `opentaiji_actor_mailbox_size`: Actor 邮箱大小

### Grafana 仪表盘

访问 `http://localhost:3001` 查看 Grafana（默认账号 admin/admin）。

### 日志查询

使用 Loki 查询日志：

```bash
# 查询错误日志
{app="opentaiji"} |= "ERROR"

# 查询特定 trace
{app="opentaiji"} |= "trace_id=abc123"
```

## 安全加固

### 1. 更新依赖

```bash
npm audit fix
npm update
```

### 2. 配置防火墙

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. SSL/TLS 证书

使用 Let's Encrypt：

```bash
certbot --nginx -d api.opentaiji.io
```

### 4. 安全扫描

```bash
# 依赖漏洞扫描
npm audit

# 容器镜像扫描
docker scan opentaiji/opentaiji:1.1.0
```

## 故障排查

### 查看日志

```bash
# Docker
docker-compose logs -f opentaiji

# Kubernetes
kubectl logs -f deployment/opentaiji -n opentaiji

# 系统日志
journalctl -u opentaiji -f
```

### 健康检查

```bash
curl http://localhost:3000/health
curl http://localhost:3000/ready
curl http://localhost:3000/metrics
```

### 常见问题

**Q: 服务无法启动**
- 检查端口是否被占用
- 检查环境变量配置
- 查看日志文件

**Q: 内存不足**
- 增加系统内存
- 调整 Node.js 堆内存限制：`NODE_OPTIONS="--max-old-space-size=4096"`

**Q: 高延迟**
- 检查 Redis 连接
- 启用缓存
- 调整 Actor 并发数

## 升级指南

### 滚动升级（Kubernetes）

```bash
# 更新镜像
kubectl set image deployment/opentaiji opentaiji=opentaiji/opentaiji:1.2.0 -n opentaiji

# 监控升级状态
kubectl rollout status deployment/opentaiji -n opentaiji

# 回滚（如有问题）
kubectl rollout undo deployment/opentaiji -n opentaiji
```

### 蓝绿部署（Docker Compose）

```bash
# 启动新版本
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale opentaiji=2

# 验证新版本
# 切换流量到新版本

# 停止旧版本
docker-compose stop opentaiji_1
```

## 性能优化

### 1. Node.js 优化

```bash
# 启用集群模式
NODE_ENV=production node dist/cluster.js

# 调整 V8 参数
NODE_OPTIONS="--max-old-space-size=4096 --optimize-for-size"
```

### 2. 系统优化

```bash
# 增加文件描述符限制
ulimit -n 65535

# 优化 TCP 参数
sysctl -w net.core.somaxconn=65535
sysctl -w net.ipv4.tcp_max_syn_backlog=65535
```

## 备份与恢复

### 数据库备份

```bash
# Redis 备份
redis-cli BGSAVE

# 配置文件备份
tar -czf backup-$(date +%Y%m%d).tar.gz config/ .env.production
```

### 恢复

```bash
# 恢复配置
tar -xzf backup-20240101.tar.gz

# 重启服务
docker-compose restart
```

## 许可证

商业软件 - 需授权使用

## 支持

- 文档：https://docs.opentaiji.io
- 问题：https://github.com/xiejianjun000/open-taiji/issues
- 邮箱：support@opentaiji.io
