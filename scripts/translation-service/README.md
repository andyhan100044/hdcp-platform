# 自动翻译服务 - DeepL API + LLM 校核

## 🚀 功能特性

- ✅ **DeepL API 集成**：使用业界领先的翻译 API
- ✅ **LLM 质量校核**：GPT-4 自动评估翻译质量
- ✅ **批量处理**：支持大规模翻译任务
- ✅ **质量评分**：0-1 分评分系统
- ✅ **自动审核**：80 分以上自动通过
- ✅ **详细报告**：生成翻译质量报告
- ✅ **文化适配**：特别优化阿拉伯语等 RTL 语言

## 📦 安装依赖

```bash
npm install axios openai ts-node
# 或
yarn add axios openai ts-node
# 或
pnpm add axios openai ts-node
```

## 🔑 配置 API 密钥

### 1. DeepL API Key

访问 [DeepL API](https://www.deepl.com/pro-api) 注册并获取 API Key：

```bash
# 免费版 (每月 50 万字符)
export DEEPL_API_KEY="your-deepl-free-api-key"

# 付费版 (无限制)
export DEEPL_API_KEY="your-deepl-pro-api-key"
```

### 2. OpenAI API Key

访问 [OpenAI Platform](https://platform.openai.com/) 获取 API Key：

```bash
export OPENAI_API_KEY="sk-your-openai-api-key"
```

## 🎯 使用方法

### 基础用法

```bash
# 1. 确保环境变量已设置
echo $DEEPL_API_KEY
echo $OPENAI_API_KEY

# 2. 运行翻译服务
npx ts-node scripts/translation-service.ts
```

### 高级用法

#### 翻译单个语言

```typescript
import { TranslationService } from './translation-service';

const service = new TranslationService();

// 只翻译中文
await service.translateSingleLocale('zh-CN');
```

#### 自定义配置

```typescript
const service = new TranslationService({
  sourceLocale: 'en',
  targetLocales: ['zh-CN', 'ja', 'ar'],
  minScore: 0.85, // 提高质量阈值
  batchSize: 30,   // 减小批次大小
});
```

## 📊 翻译流程

```
1️⃣ 提取英文原文
   ↓
2️⃣ DeepL 批量翻译
   ↓
3️⃣ LLM 质量校核
   ↓
4️⃣ 质量评分 (0-1)
   ↓
5️⃣ 自动审核 (≥0.8)
   ↓
6️⃣ 生成翻译文件
   ↓
7️⃣ 生成质量报告
```

## 📝 输出文件

运行后会生成以下文件：

```
apps/web/src/locales/
├── en.json          (原始英文)
├── zh-CN.json       (中文翻译)
├── es.json          (西班牙语翻译)
├── fr.json          (法语翻译)
├── de.json          (德语翻译)
├── ja.json          (日语翻译)
├── ko.json          (韩语翻译)
└── ar.json          (阿拉伯语翻译)

translation-report-zh-CN.md  (中文翻译报告)
translation-report-es.md     (西班牙语翻译报告)
...
translation-quality-report.md (总体质量报告)
```

## 📈 质量报告示例

### 翻译报告 (zh-CN.md)
```markdown
================================
翻译报告 - zh-CN
================================
总计翻译: 156
自动通过: 142
失败/需人工: 14
平均分: 0.87/1.0

需人工审核的翻译:
- nav.home: 首页 (分: 0.65)
- carbon.projectName: 项目名称 (分: 0.72)
```

### 质量总报告
```markdown
# 翻译质量报告

## 总体统计
- 总翻译数: 1092
- 优秀 (≥0.9): 687 (62.9%)
- 良好 (0.7-0.89): 312 (28.6%)
- 一般 (0.5-0.69): 78 (7.1%)
- 差 (<0.5): 15 (1.4%)
```

## ⚙️ 配置选项

### 环境变量

| 变量名 | 必需 | 说明 |
|--------|------|------|
| `DEEPL_API_KEY` | ✅ | DeepL API 密钥 |
| `OPENAI_API_KEY` | ✅ | OpenAI API 密钥 |
| `DEEPL_API_URL` | ❌ | DeepL API 端点 (默认: 免费版) |

### 脚本配置

```typescript
const config = {
  sourceLocale: 'en',           // 源语言
  targetLocales: [              // 目标语言列表
    'zh-CN', 'es', 'fr', 'de',
    'ja', 'ko', 'ar'
  ],
  outputDir: 'apps/web/src/locales', // 输出目录
  minScore: 0.8,               // 最小通过分数
  batchSize: 50,                // 批处理大小
  maxRetries: 3,                // 最大重试次数
  delayBetweenBatches: 1000,    // 批次间延迟 (毫秒)
};
```

## 🌍 特殊语言支持

### 阿拉伯语 (ar) 特殊优化

系统会自动对阿拉伯语翻译进行特殊检查：

- ✅ RTL (从右到左) 布局适配
- ✅ 文化敏感内容过滤 (酒精、猪肉、彩虹元素)
- ✅ 数字格式验证 (使用 0-9 而非 ٠١٢)
- ✅ 日期格式检查 (DD/MM/YYYY)
- ✅ 断词和换行优化

```typescript
// 自动检测并应用阿语特殊规则
if (locale === 'ar') {
  applyRTLFormatting(translation);
  filterCulturalContent(translation);
  validateNumberFormat(translation);
}
```

## 💰 成本估算

### DeepL API
- **免费版**: 每月 50 万字符 ≈ $0
- **付费版**: 每字符 $0.00002

### OpenAI API
- **GPT-4 Turbo**: 每 1K tokens ≈ $0.01

### 示例成本 (1000 个翻译键)
- DeepL: ~$0.50
- OpenAI: ~$2.00
- **总计**: ~$2.50

## 🔧 故障排除

### 常见错误

#### 1. API 密钥未设置
```bash
Error: DEEPL_API_KEY 未设置
```
**解决方案**:
```bash
export DEEPL_API_KEY="your-api-key"
```

#### 2. 翻译超时
```bash
Error: DeepL 翻译失败: timeout
```
**解决方案**: 增加 `timeout` 配置或减小 `batchSize`

#### 3. LLM 校核失败
```bash
Error: LLM 校核失败: rate limit
```
**解决方案**: 增加批次间延迟时间

## 📚 参考文档

- [DeepL API 文档](https://www.deepl.com/docs-api)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [项目 i18n 实现文档](../hdcp-platform-repo/I18N_IMPLEMENTATION.md)

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

MIT License

## 🆘 支持

如有问题，请提交 [GitHub Issue](https://github.com/your-org/hdcp-platform/issues)

---

**提示**: 首次运行建议只翻译 1-2 种语言测试，确认质量后再批量翻译所有语言。
