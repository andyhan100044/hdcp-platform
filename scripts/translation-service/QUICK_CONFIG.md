# ⚡ 5分钟配置指南

## 🎯 选择你的 LLM 方案

### 方案 1: 企业级 (推荐 ⭐⭐⭐⭐⭐)
```
质量最高，成本中等，适合正式项目
```

**配置**:
```bash
# 必需
export DEEPL_API_KEY="your-deepl-key"

# LLM (选择其一或组合)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# 运行
npm run translate:v2
```

**成本**: ~$0.025/翻译
**质量**: 9.5/10

---

### 方案 2: 性价比 (推荐 ⭐⭐⭐⭐)
```
成本低，中文优化好，适合批量翻译
```

**配置**:
```bash
# 必需
export DEEPL_API_KEY="your-deepl-key"

# LLM
export ZHIPU_API_KEY="your-zhipu-key"

# 运行
npm run translate:v2
```

**成本**: ~$0.009/翻译
**质量**: 8/10

---

### 方案 3: 多提供商负载均衡 (推荐 ⭐⭐⭐⭐⭐)
```
稳定性最高，质量有保障
```

**配置**:
```bash
# 必需
export DEEPL_API_KEY="your-deepl-key"

# LLM 组合
export OPENAI_API_KEY="sk-..."
export ZHIPU_API_KEY="your-zhipu-key"
export GOOGLE_API_KEY="..."

# 负载均衡
export LLM_PROVIDERS="openai,zhipu,google"
export ENABLE_LOAD_BALANCING=true

# 运行
npm run translate:v2 -- --load-balance
```

**成本**: ~$0.015/翻译
**质量**: 9/10

---

### 方案 4: 中文专精 (推荐 ⭐⭐⭐⭐)
```
对中文理解最好
```

**配置**:
```bash
# 必需
export DEEPL_API_KEY="your-deepl-key"

# LLM
export ZHIPU_API_KEY="your-zhipu-key"
export BAIDU_API_KEY="your-baidu-key"
export BAIDU_SECRET_KEY="your-baidu-secret"

# 运行
npm run translate:v2
```

**成本**: ~$0.008/翻译
**中文质量**: 10/10

---

## 🚀 快速开始

### 步骤 1: 选择方案并配置
```bash
# 复制上方任意方案配置
export DEEPL_API_KEY="your-deepl-key"
# ... 其他配置
```

### 步骤 2: 测试连接
```bash
cd scripts

# 测试 DeepL
npm run test:connection

# 测试 LLM
npm run test:llm
```

### 步骤 3: 运行翻译
```bash
# 快速翻译 (所有语言)
npm run translate:v2

# 只翻译特定语言
npm run translate:v2 -- --locales=zh-CN,ja,ar

# 提高质量阈值
npm run translate:v2 -- --min-score=0.9
```

---

## 📦 安装依赖

```bash
cd scripts
npm install
```

---

## 🔑 API 密钥获取

### DeepL (必需)
1. 访问: https://www.deepl.com/pro-api
2. 注册账号
3. 获取 API Key
4. 免费版: 每月 50 万字符

### OpenAI (可选)
1. 访问: https://platform.openai.com/
2. 注册/登录
3. 创建 API Key
4. 建议充值 $5-10

### Anthropic (可选)
1. 访问: https://console.anthropic.com/
2. 注册/登录
3. 创建 API Key
4. 免费试用额度

### 智谱 (可选)
1. 访问: https://open.bigmodel.cn/
2. 注册/登录
3. 创建 API Key
4. 免费试用额度

### 百度文心 (可选)
1. 访问: https://console.bce.baidu.com/
2. 注册/登录
3. 创建应用
4. 获取 API Key 和 Secret Key

### Google Gemini (可选)
1. 访问: https://aistudio.google.com/
2. 注册/登录
3. 创建 API Key
4. 免费试用额度

---

## 🎯 不同场景推荐

### 开发测试
```bash
# 成本最低
export ZHIPU_API_KEY="..."
npm run translate:v2 -- --locales=zh-CN
```

### 小型企业项目
```bash
# 质量与成本平衡
export OPENAI_API_KEY="sk-..."
export ZHIPU_API_KEY="..."
npm run translate:v2 -- --llm-providers=openai,zhipu
```

### 大型企业项目
```bash
# 最佳质量
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
npm run translate:v2 -- --load-balance
```

### 阿拉伯语项目
```bash
# 阿语优化
export ANTHROPIC_API_KEY="sk-ant-..."
npm run translate:v2 -- --locales=ar --min-score=0.85
```

---

## ⚙️ 高级配置

### 自定义批处理大小
```bash
npm run translate:v2 -- --batch-size=30
```

### 仅翻译特定语言
```bash
npm run translate:v2 -- --locales=zh-CN,ja,ko
```

### 组合使用
```bash
npm run translate:v2 \
  --locales=zh-CN,ja,ar \
  --min-score=0.85 \
  --batch-size=30 \
  --load-balance
```

---

## 📊 查看结果

```bash
# 查看质量报告
cat translation-quality-report-v2.md

# 查看特定语言报告
cat translation-report-zh-CN.md
```

---

## 🐛 常见问题

### Q: API 密钥无效
```bash
# 检查环境变量
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# 重新设置
export OPENAI_API_KEY="sk-新的密钥"
```

### Q: 翻译失败
```bash
# 检查 DeepL 连接
curl -X POST https://api-free.deepl.com/v2/translate \
  -H "Authorization: DeepL-Auth-Key $DEEPL_API_KEY" \
  -d "text=Hello&target_lang=ZH"

# 检查 LLM 连接
npm run test:llm
```

### Q: 成本太高
```bash
# 降低质量阈值
npm run translate:v2 -- --min-score=0.7

# 使用更便宜的 LLM
export ZHIPU_API_KEY="..."
```

### Q: 质量不够
```bash
# 提高质量阈值
npm run translate:v2 -- --min-score=0.9

# 使用更好的 LLM
export ANTHROPIC_API_KEY="..."
```

---

## 💡 小贴士

1. **首次使用**: 建议只翻译 1-2 种语言测试
2. **节省成本**: 批量翻译，使用批量 API
3. **提高质量**: 使用多个 LLM 负载均衡
4. **阿拉伯语**: 单独设置更高质量阈值
5. **监控成本**: 定期查看 API 使用量

---

## 📞 需要帮助？

- 📚 完整文档: `README.md`
- 🎯 提供商指南: `LLM_PROVIDER_GUIDE.md`
- 📊 方案对比: `COMPARISON.md`
- 🔄 流程图: `FLOWCHART.md`

---

**🚀 现在开始配置你的翻译服务吧！**
