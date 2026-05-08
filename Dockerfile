# OpenTaiji 生产级 Docker 镜像
# 多阶段构建，优化镜像大小和安全性

# 阶段1: 依赖安装
FROM node:20-alpine AS deps
WORKDIR /app

# 安装必要的系统依赖
RUN apk add --no-cache libc6-compat python3 make g++

# 复制 package 文件
COPY package*.json ./
COPY output/p-mo6gxim524edn6-worker3/package*.json ./output/p-mo6gxim524edn6-worker3/

# 安装依赖
RUN npm ci --only=production && npm cache clean --force

# 阶段2: 构建
FROM node:20-alpine AS builder
WORKDIR /app

# 安装构建依赖
RUN apk add --no-cache python3 make g++

# 复制依赖
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/output/p-mo6gxim524edn6-worker3/node_modules ./output/p-mo6gxim524edn6-worker3/node_modules

# 复制源代码
COPY . .

# 构建应用
RUN cd output/p-mo6gxim524edn6-worker3 && npm run build

# 阶段3: 生产运行
FROM node:20-alpine AS runner
WORKDIR /app

# 创建非 root 用户
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 opentaiji

# 设置环境变量
ENV NODE_ENV=production
ENV PORT=3000
ENV LOG_LEVEL=info

# 安装生产环境必要的系统依赖
RUN apk add --no-cache dumb-init curl

# 复制构建产物
COPY --from=builder --chown=opentaiji:nodejs /app/output/p-mo6gxim524edn6-worker3/dist ./dist
COPY --from=builder --chown=opentaiji:nodejs /app/output/p-mo6gxim524edn6-worker3/node_modules ./node_modules
COPY --from=builder --chown=opentaiji:nodejs /app/output/p-mo6gxim524edn6-worker3/package*.json ./

# 复制配置文件
COPY --chown=opentaiji:nodejs config/ ./config/

# 创建日志目录
RUN mkdir -p /app/logs && chown -R opentaiji:nodejs /app/logs

# 切换到非 root 用户
USER opentaiji

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# 暴露端口
EXPOSE 3000

# 使用 dumb-init 处理信号
ENTRYPOINT ["dumb-init", "--"]

# 启动命令
CMD ["node", "dist/index.js"]
