# 🚀 快速开始指南

## ⚡ 5分钟快速体验

### 步骤 1: 获取 API 密钥 (2分钟)

#### DeepL API
```bash
# 访问 https://www.deepl.com/pro-api
# 免费版: 每月 50 万字符
# 注册后获取 API Key
```

#### OpenAI API
```bash
# 访问 https://platform.openai.com/
# 注册后获取 API Key
```

### 步骤 2: 设置环境变量 (1分钟)

```bash
# 在项目根目录执行
export DEEPL_API_KEY="your-deepl-api-key-here"
export OPENAI_API_KEY="your-openai-api-key-here"

# 验证设置
echo $DEEPL_API_KEY
echo $OPENAI_API_KEY
```

### 步骤 3: 测试连接 (1分钟)

```bash
cd scripts
npx ts-node test-connection.ts
```

**期望输出**:
```
✅ DeepL API 连接成功
✅ OpenAI API 连接成功
✅ 找到英文翻译文件
🎉 所有测试通过！
```

### 步骤 4: 运行翻译 (1分钟)

```bash
# 选择快速体验 (只翻译中文和日语)
npm run translate:quick
```

或手动运行:
```bash
npx ts-node translation-service.ts
```

---

## 📦 完整安装

### 1. 安装依赖

```bash
# 在 scripts 目录执行
cd scripts

# 使用 npm
npm install

# 或使用 yarn
yarn install

# 或使用 pnpm
pnpm install
```

### 2. 验证环境

```bash
# 检查 Node.js 版本 (需要 ≥ 18)
node --version

# 检查 API 密钥
./start-translation.sh
```

---

## 🎯 常用命令

### 基本命令

```bash
# 翻译全部语言
npm run translate

# 交互式翻译 (可选择语言)
npm run translate:quick

# 测试 API 连接
npm run test:connection

# 查看质量报告
npm run report:quality
```

### 高级用法

```bash
# 只翻译指定语言
npx ts-node translation-service.ts --locales=zh-CN,ja,ar

# 调整质量阈值
npx ts-node translation-service.ts --min-score=0.9

# 查看帮助
npx ts-node translation-service.ts --help
```

---

## 🔧 配置选项

### 1. 环境变量配置

创建 `.env` 文件:

```bash
# DeepL 配置
DEEPL_API_KEY=your-key-here
DEEPL_API_URL=https://api-free.deepl.com/v2/translate

# OpenAI 配置
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# 翻译配置
SOURCE_LOCALE=en
TARGET_LOCALES=zh-CN,es,fr,de,ja,ko,ar
MIN_SCORE=0.8
BATCH_SIZE=50
```

### 2. 代码配置

编辑 `translation-service.ts`:

```typescript
const config = {
  sourceLocale: 'en',
  targetLocales: ['zh-CN', 'es', 'fr', 'de', 'ja', 'ko', 'ar'],
  minScore: 0.8,        // 最小通过分数
  batchSize: 50,        // 批处理大小
  maxRetries: 3,        // 最大重试次数
  delayBetweenBatches: 1000,  // 批次间延迟 (毫秒)
};
```

---

## 📊 示例输出

### 控制台输出

```
🌍 HDCP 自动翻译服务
✅ 环境变量检查通过

请选择翻译范围:
1) 全部语言 (zh-CN, es, fr, de, ja, ko, ar)
2) 仅亚洲语言 (zh-CN, ja, ko)
3) 仅欧洲语言 (es, fr, de)
4) 自定义语言

请输入选择 (1-4): 2

🌏 翻译亚洲语言...
✅ 已设置自定义语言: zh-CN,ja,ko

🔄 开始翻译到 zh-CN...
处理批次 1/4
处理批次 2/4
...
✅ zh-CN 翻译完成并保存

🔄 开始翻译到 ja...
...
✅ ja 翻译完成并保存

🎉 所有翻译完成！

📁 生成的文件:
  - apps/web/src/locales/*.json
  - translation-report-*.md
  - translation-quality-report.md
```

### 质量报告示例

```
translation-report-zh-CN.md
═══════════════════════════════

翻译报告 - zh-CN
────────────────────────────────
总计翻译: 156
自动通过: 142 (91.0%)
失败/需人工: 14 (9.0%)
平均分: 0.87/1.0

✅ 优秀翻译 (≥0.9): 98 个
✅ 良好翻译 (0.7-0.89): 44 个
⚠️  需改进翻译 (<0.7): 14 个

需人工审核的翻译:
- nav.home: 首页 (分: 0.65)
- carbon.projectName: 项目名称 (分: 0.72)

问题统计:
- 术语不一致: 5 次
- 表达不够自然: 4 次
- 格式问题: 3 次
- 文化适配问题: 2 次
```

---

## ⚠️ 常见问题

### Q1: API 密钥错误

```
❌ 错误: DEEPL_API_KEY 未设置
```

**解决方案**:
```bash
export DEEPL_API_KEY="your-actual-api-key"
echo $DEEPL_API_KEY  # 验证设置
```

### Q2: 翻译超时

```
Error: DeepL 翻译失败: timeout
```

**解决方案**:
- 增加 `timeout` 配置
- 减小 `batchSize` (从 50 改为 30)
- 检查网络连接

### Q3: LLM 校核失败

```
Error: LLM 校核失败: rate limit
```

**解决方案**:
- 增加批次间延迟: `delayBetweenBatches: 2000`
- 减小并发数: `batchSize: 30`
- 升级 OpenAI API 套餐

### Q4: 阿拉伯语质量差

```
阿语通过率只有 65.4%
```

**解决方案**:
- 降低阿语的质量阈值: `arabicMinScore: 0.6`
- 加强人工审核
- 添加阿语特殊规则

---

## 🎓 下一步

### 1. 验证翻译质量
```bash
# 查看质量报告
cat translation-quality-report.md

# 检查特定语言
cat translation-report-ar.md
```

### 2. 手动审核
- 打开 `translation-report-*.md` 文件
- 找到标记为 "需人工审核" 的翻译
- 手动更新对应文件
- 重新运行验证

### 3. 集成到 CI/CD
```yaml
# .github/workflows/translation.yml
name: Auto Translation
on:
  schedule:
    - cron: '0 0 * * 0'  # 每周日运行
jobs:
  translate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm install
      - name: Run translation
        env:
          DEEPL_API_KEY: ${{ secrets.DEEPL_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: npm run translate
```

### 4. 优化翻译质量
- 分析质量报告
- 调整 LLM 提示词
- 更新 DeepL 参数
- 添加专业术语库

---

## 📞 获取帮助

- 📚 完整文档: [README.md](README.md)
- 🔄 流程图: [FLOWCHART.md](FLOWCHART.md)
- 📊 方案对比: [COMPARISON.md](COMPARISON.md)
- 🐛 提交问题: [GitHub Issues](https://github.com/your-org/hdcp-platform/issues)

---

**快速提示**: 首次使用建议只翻译 1-2 种语言，验证效果后再批量翻译所有语言。
