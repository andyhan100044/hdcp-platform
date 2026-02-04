# Nginx 部署方式说明

## ✅ 答案：不需单独部署！

### 🚀 集成部署 (推荐)

**Nginx 已经集成在 docker-compose.yml 中！**

```yaml
# docker-compose.yml
services:
  postgres:    # 数据库
  redis:      # 缓存
  api:        # 后端 API
  web:        # 前端
  cms:        # CMS
  nginx:      # ← Nginx 也在里面！
  grafana:    # 监控
```

**只需要一个命令:**

```bash
docker-compose up -d
```

---

## 🔄 对比两种方式

### 方式1: 集成部署 (我们用的)

```
所有服务都在 docker-compose.yml 中:
├── postgres (数据库)
├── redis (缓存)
├── api (后端)
├── web (前端)
├── cms (CMS)
└── nginx (反向代理)

优点:
✅ 一个命令启动所有服务
✅ 统一管理
✅ 自动重启
✅ 网络自动配置
✅ 简单!

命令:
docker-compose up -d
```

### 方式2: 单独部署 (不推荐)

```
Nginx 需要单独配置:
docker-compose up -d
# 然后单独配置 Nginx...

需要单独配置文件:
├── /etc/nginx/nginx.conf  ← 手动配置
├── /etc/nginx/sites-enabled/  ← 手动配置
└── nginx -s reload  ← 手动重启

缺点:
❌ 需要专业知识
❌ 容易出错
❌ 复杂
❌ 不推荐新手使用
```

---

## 🎯 我们的配置

### docker-compose.yml 中的 Nginx

```yaml
nginx:
  image: nginx:alpine              # 使用官方 Nginx 镜像
  container_name: hdcp-nginx        # 容器名
  ports:                            # 端口映射
    - "80:80"                       # HTTP
    - "443:443"                     # HTTPS
  volumes:                          # 挂载配置
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    - ./nginx/ssl:/etc/nginx/ssl
  depends_on:                       # 依赖服务
    - web
    - api
    - cms
  networks:                        # 网络
    - hdcp-network
  restart: unless-stopped          # 自动重启
```

### Nginx 配置文件

```nginx
# nginx/nginx.conf
server {
    listen 80;
    server_name localhost;

    # 前端路由
    location / {
        proxy_pass http://web:3000;
    }

    # API 路由
    location /api/ {
        proxy_pass http://api:8000;
    }

    # GraphQL 路由
    location /graphql {
        proxy_pass http://api:8000;
    }

    # CMS 路由
    location /cms/ {
        proxy_pass http://cms:1337/;
    }
}
```

---

## ⚡ 启动方式

### 一键启动所有服务

```bash
# 启动所有服务 (包括 Nginx)
docker-compose up -d

# 查看状态
docker-compose ps

# 查看 Nginx 日志
docker-compose logs nginx
```

### 访问方式

```
启动后可以访问:

http://localhost         ← 前端
http://localhost/api     ← API
http://localhost/graphql ← GraphQL
http://localhost/cms     ← CMS 管理后台
```

---

## 🔍 验证 Nginx 正在运行

### 查看容器

```bash
docker-compose ps

# 应该看到:
# NAME           SERVICE   STATUS
# hdcp-nginx     nginx     Up
# hdcp-api       api       Up
# hdcp-web       web       Up
# ...
```

### 查看 Nginx 日志

```bash
docker-compose logs nginx

# 应该看到:
# nginx: configuration file /etc/nginx/nginx.conf test is successful
# nginx: configuration file /etc/nginx/nginx.conf is valid
```

### 测试 Nginx 配置

```bash
# 进入 Nginx 容器
docker-compose exec nginx nginx -t

# 应该看到:
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

---

## 🎨 高级配置

### 添加 HTTPS

```nginx
# nginx/nginx.conf
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # ... 其他配置
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### 启用 Gzip 压缩

```nginx
# nginx/nginx.conf
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types
    text/plain
    text/css
    text/xml
    text/javascript
    application/javascript
    application/xml+rss;
```

### 添加缓存

```nginx
# nginx/nginx.conf
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

## 🔧 常用操作

### 重启 Nginx

```bash
docker-compose restart nginx
```

### 重新加载配置

```bash
docker-compose exec nginx nginx -s reload
```

### 查看配置

```bash
docker-compose exec nginx cat /etc/nginx/nginx.conf
```

### 编辑配置

```bash
# 修改配置文件
nano nginx/nginx.conf

# 重新加载配置
docker-compose exec nginx nginx -s reload
```

---

## ❓ 常见问题

### Q: 为什么看不到 Nginx 端口 80？

**A:** 检查是否启动了 Nginx

```bash
# 查看容器
docker-compose ps

# 如果没有 nginx，检查 docker-compose.yml
# 确保 services 部分有 nginx:
```

---

### Q: 可以修改 Nginx 端口吗？

**A:** 可以，修改 docker-compose.yml

```yaml
nginx:
  ports:
    - "8080:80"    # 改为 8080
    - "8443:443"    # 改为 8443
```

---

### Q: 如何禁用 Nginx？

**A:** 注释掉或删除 Nginx 部分

```yaml
# services:
#   nginx:
#     # 注释掉 Nginx 服务
```

---

## ✨ 总结

### ✅ 我们使用集成部署

- **Nginx 在 docker-compose.yml 中**
- **一个命令启动所有服务**
- **自动网络配置**
- **自动重启**
- **新手友好**

### 🚀 启动命令

```bash
docker-compose up -d
```

### 📍 访问地址

- http://localhost - 前端
- http://localhost/api - API
- http://localhost/cms - CMS

---

**记住**: Nginx 已经集成在 docker-compose 中，不需要单独部署！
