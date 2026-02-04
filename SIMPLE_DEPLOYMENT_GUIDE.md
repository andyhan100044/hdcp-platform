# 🚀 HDCP - 超简单部署指南

## 3种部署方式

### 🏠 方式1: 本地测试 (最简单)

```
用户 → 电脑上的服务

直接访问:
http://localhost:3000  ← 前端
http://localhost:8000  ← API
http://localhost:1337  ← CMS

命令:
docker-compose -f simple.yml up -d
```

**适合:** 新手、快速测试、学习

---

### ☁️ 方式2: 云服务器 (推荐)

```
用户 → 互联网 → 云服务器

通过域名访问:
http://yourdomain.com  ← 前端 (统一入口)
http://yourdomain.com/api  ← API
http://yourdomain.com/cms  ← CMS

命令:
docker-compose up -d
```

**适合:** 公网展示、客户演示

---

### 🌍 方式3: 生产环境 (最完整)

```
用户 → CDN → 负载均衡 → Nginx → 各个服务

HTTPS 访问:
https://yourdomain.com  ← 前端
https://yourdomain.com/api  ← API
https://yourdomain.com/cms  ← CMS

命令:
docker-compose up -d
```

**适合:** 真实生产、公网部署

---

## 🤔 Nginx 是啥？

### 简单理解

**Nginx = 门卫 + 交通指挥员**

```
没有 Nginx:
用户 → 多个门 (3000, 8000, 1337) ← 麻烦!

有 Nginx:
用户 → 一个门 (80/443) → Nginx → 各个服务 ← 简单!
```

### Nginx 的作用

| 作用 | 比喻 | 好处 |
|------|------|------|
| **反向代理** | 门卫 | 隐藏内部服务 |
| **负载均衡** | 交通指挥 | 分发请求 |
| **SSL证书** | 安检 | HTTPS加密 |
| **缓存** | 临时仓库 | 加快访问 |
| **压缩** | 真空包装 | 节省流量 |

---

## 🎯 选择哪种方式？

### 根据你的需求

```
我要:
├─ 只是试试 → 方式1 (本地测试) ✅
├─ 演示给客户 → 方式2 (云服务器) ✅
└─ 真正上线 → 方式3 (生产环境) ✅
```

### 快速决策

| 你的情况 | 推荐 | 原因 |
|----------|------|------|
| **第一次用** | 方式1 | 最简单 |
| **给朋友看** | 方式2 | 真实可用 |
| **客户使用** | 方式3 | 安全稳定 |

---

## ⚡ 3个命令启动

### 方式1: 本地测试

```bash
# 1. 进入项目目录
cd hdcp-template

# 2. 启动 (简化版)
docker-compose -f simple.yml up -d

# 3. 访问
# 浏览器打开: http://localhost:3000
```

### 方式2: 云服务器

```bash
# 1. 进入项目目录
cd hdcp-template

# 2. 启动 (完整版)
docker-compose up -d

# 3. 配置域名
# 在域名商处设置 A 记录指向服务器IP

# 4. 访问
# 浏览器打开: http://yourdomain.com
```

### 方式3: 生产环境

```bash
# 1. 进入项目目录
cd hdcp-template

# 2. 配置 SSL 证书
# 申请 Let's Encrypt 证书

# 3. 启动
docker-compose up -d

# 4. 访问
# 浏览器打开: https://yourdomain.com
```

---

## 📋 详细对比

| 特性 | 方式1: 本地 | 方式2: 云服务器 | 方式3: 生产 |
|------|-------------|----------------|-------------|
| **端口** | 3000, 8000, 1337 | 统一 80 端口 | 统一 443 端口 |
| **访问** | localhost | yourdomain.com | yourdomain.com |
| **HTTPS** | ❌ | 可选 | ✅ 必须 |
| **Nginx** | ❌ | ✅ | ✅ |
| **复杂度** | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| **安全性** | 低 | 中 | 高 |
| **适合** | 测试 | 演示 | 生产 |

---

## 🔍 常见问题

### Q: 我是新手，应该用哪种？

**A:** 方式1 - 本地测试
```bash
# 最简单，一学就会
docker-compose -f simple.yml up -d
```

---

### Q: 方式1 和 方式2 有什么区别？

**A:**
```
方式1: 多个门
http://localhost:3000  (前端)
http://localhost:8000  (API)
http://localhost:1337  (CMS)

方式2: 一个门
http://yourdomain.com  (全部通过这里)
```

---

### Q: 必须配置 Nginx 吗？

**A:** 看情况

| 环境 | 必须? | 说明 |
|------|--------|------|
| **本地测试** | ❌ 不是 | 可以直接访问端口 |
| **云服务器** | ✅ 是的 | 需要公网访问 |
| **生产环境** | ✅ 是的 | 必须有HTTPS |

---

### Q: Nginx 会影响速度吗？

**A:** 不会！Nginx 会让网站**更快**

- ✅ 缓存静态文件
- ✅ 压缩传输数据
- ✅ 负载均衡
- ✅ 防DDoS攻击

---

## 🎓 学习路径

### 第1步: 本地测试 (新手)
```bash
docker-compose -f simple.yml up -d
```
学习基础功能

---

### 第2步: 云服务器 (进阶)
```bash
docker-compose up -d
```
学会部署

---

### 第3步: 生产环境 (专家)
```bash
# 配置 SSL + 监控 + 备份
docker-compose up -d
```
掌握运维

---

## 📞 快速帮助

### 启动服务
```bash
cd hdcp-template
docker-compose up -d
```

### 查看状态
```bash
docker-compose ps
```

### 查看日志
```bash
docker-compose logs -f
```

### 停止服务
```bash
docker-compose down
```

### 重启服务
```bash
docker-compose restart
```

---

## ✨ 一句话总结

**Nginx = 生产环境的必需品**

- 本地测试: 可有可无
- 云服务器: 推荐使用
- 生产环境: 必须使用

**新手从方式1开始，专业从方式2开始！** 🚀
