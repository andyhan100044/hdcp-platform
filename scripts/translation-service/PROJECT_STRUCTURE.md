# 📁 项目结构

```
scripts/                              # 翻译服务根目录
│
├── 📄 translation-service.ts        # ⭐ 主服务入口
├── 📄 types.ts                      # 📋 类型定义
├── 📄 package.json                  # 📦 NPM 配置
│
├── 🔌 providers/                    # API 提供者模块
│   ├── 📄 deepl.ts                  #   DeepL API 集成
│   └── 📄 llm-reviewer.ts           #   LLM 校核模块
│
├── 🔧 tools/                        # 工具脚本
│   ├── 📄 test-connection.ts        #   API 连接测试
│   └── 📄 start-translation.sh      #   快速启动脚本
│
└── 📚 docs/                         # 文档目录
    ├── 📄 README.md                 #   完整文档
    ├── 📄 QUICK_START.md            #   快速开始指南
    ├── 📄 COMPARISON.md             #   方案对比
    └── 📄 FLOWCHART.md             #   流程图详解
```

---

## 📄 核心文件说明

### ⭐ 主服务文件

#### `translation-service.ts`
**功能**: 核心翻译服务
**职责**:
- 提取英文原文
- 协调 DeepL 翻译
- 调用 LLM 校核
- 生成翻译文件
- 生成质量报告

**使用**:
```bash
npx ts-node translation-service.ts
```

#### `providers/deepl.ts`
**功能**: DeepL API 封装
**职责**:
- 单个文本翻译
- 批量翻译优化
- 支持语言列表
- 错误处理

**使用**:
```typescript
import { translateWithDeepL } from './providers/deepl';
const result = await translateWithDeepL('Hello', 'en', 'zh-CN');
```

#### `providers/llm-reviewer.ts`
**功能**: LLM 质量校核
**职责**:
- GPT-4 质量评估
- 多维度评分
- 翻译改进建议
- 批量校核优化

**使用**:
```typescript
import { reviewWithLLM } from './providers/llm-reviewer';
const result = await reviewWithLLM('Hello', '你好', 'zh-CN', 'greeting.hello');
```

---

## 🔧 工具文件

### `test-connection.ts`
**功能**: API 连接测试
**测试项目**:
- ✅ DeepL API 连接
- ✅ OpenAI API 连接
- ✅ 文件系统访问
- ✅ 英文原文文件

**使用**:
```bash
npx ts-node test-connection.ts
```

### `start-translation.sh`
**功能**: 交互式启动脚本
**特性**:
- 🎯 语言选择菜单
- ✅ 环境变量检查
- 🚀 自动运行翻译
- 📊 实时进度显示

**使用**:
```bash
./start-translation.sh
```

---

## 📚 文档文件

### `README.md`
**内容**: 完整技术文档
**章节**:
- 功能特性
- 安装配置
- 使用方法
- API 参考
- 成本估算
- 故障排除

### `QUICK_START.md`
**内容**: 5 分钟快速体验
**章节**:
- 获取 API 密钥
- 环境设置
- 测试连接
- 运行翻译
- 常见问题

### `COMPARISON.md`
**内容**: 方案对比分析
**对比维度**:
- 翻译来源
- 质量控制
- 扩展性
- 维护成本
- 成本分析
- 实施建议

### `FLOWCHART.md`
**内容**: 详细流程图
**图表**:
- 完整流程图
- 并行处理时序
- 性能优化点
- 错误处理流程
- 质量保证流程
- 阿语特殊处理

---

## 🔄 数据流

```
📥 输入
└── apps/web/src/locales/en.json
    │
    ▼
🔄 处理
├── 1️⃣ 提取原文
├── 2️⃣ DeepL 翻译
├── 3️⃣ LLM 校核
├── 4️⃣ 质量筛选
└── 5️⃣ 文件生成
    │
    ▼
📤 输出
├── apps/web/src/locales/{locale}.json
├── translation-report-{locale}.md
└── translation-quality-report.md
```

---

## ⚙️ 配置层次

### 1️⃣ 环境变量 (最高优先级)
```bash
DEEPL_API_KEY=xxx
OPENAI_API_KEY=xxx
```

### 2️⃣ 命令行参数
```bash
npx ts-node translation-service.ts --locales=zh-CN,ja --min-score=0.9
```

### 3️⃣ 代码配置 (默认)
```typescript
const config = {
  sourceLocale: 'en',
  targetLocales: ['zh-CN', 'es', 'fr', 'de', 'ja', 'ko', 'ar'],
  minScore: 0.8,
  batchSize: 50,
};
```

---

## 📊 依赖关系

```
translation-service.ts
    │
    ├── types.ts (类型定义)
    │
    ├── providers/
    │   ├── deepl.ts
    │   │   └── axios (HTTP 请求)
    │   │
    │   └── llm-reviewer.ts
    │       └── openai (GPT-4 调用)
    │
    └── tools/
        ├── test-connection.ts
        └── start-translation.sh
```

---

## 🎯 扩展点

### 添加新语言
```typescript
// 1. 更新 targetLocales
const targetLocales = [..., 'new-lang'];

// 2. 添加语言上下文 (可选)
const localeContext = {
  'new-lang': { name: 'New Language' }
};

// 3. 添加特殊规则 (可选)
if (locale === 'new-lang') {
  applySpecialRules(translation);
}
```

### 添加新翻译提供商
```typescript
// 1. 创建 provider
// providers/google-translate.ts

// 2. 在 translation-service.ts 中切换
const provider = process.env.TRANSLATION_PROVIDER || 'deepl';
```

### 自定义质量检查
```typescript
// 在 llm-reviewer.ts 中添加新规则
const customChecks = {
  financialTerms: checkFinancialTerms,
  legalTerms: checkLegalTerms,
  brandTerms: checkBrandTerms,
};
```

---

## 🚀 部署建议

### 开发环境
```bash
# 本地运行
cd scripts
npm install
npm run translate:quick
```

### CI/CD 环境
```yaml
# GitHub Actions
- name: Run Translation
  env:
    DEEPL_API_KEY: ${{ secrets.DEEPL_API_KEY }}
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    cd scripts
    npm install
    npm run translate
```

### Docker 容器
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY scripts/ ./scripts/
RUN cd scripts && npm install
CMD ["npm", "run", "translate"]
```

---

## 📦 目录树

```
scripts/
│
├── 📄 translation-service.ts       ⭐ 主服务 (核心逻辑)
├── 📄 types.ts                     📋 类型定义
├── 📄 package.json                  📦 依赖配置
│
├── 🔌 providers/
│   ├── 📄 deepl.ts                 🔑 DeepL API
│   └── 📄 llm-reviewer.ts          🤖 LLM 校核
│
├── 🔧 tools/
│   ├── 📄 test-connection.ts       🔍 连接测试
│   └── 📄 start-translation.sh     🚀 快速启动
│
└── 📚 docs/
    ├── 📄 README.md                📖 完整文档
    ├── 📄 QUICK_START.md           ⚡ 快速开始
    ├── 📄 COMPARISON.md            📊 方案对比
    ├── 📄 FLOWCHART.md             🔄 流程图
    └── 📄 PROJECT_STRUCTURE.md     📁 项目结构 (本文件)
```

---

**总文件数**: 11 个
**核心文件**: 3 个 (service, providers)
**工具文件**: 2 个
**文档文件**: 6 个
