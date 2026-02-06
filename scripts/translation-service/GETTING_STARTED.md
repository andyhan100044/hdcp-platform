# 🚀 Getting Started - HDCP Auto Translation Service

Welcome to the HDCP Auto Translation Service! This guide will get you up and running in 5 minutes.

## 📋 Prerequisites

- Node.js 18+
- npm or yarn
- DeepL API key (required)
- At least one LLM API key (recommended)

## ⚡ Quick Setup (5 minutes)

### Step 1: Navigate to Service
```bash
cd scripts/translation-service
```

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: Get API Keys

#### DeepL API (Required)
1. Visit: https://www.deepl.com/pro-api
2. Register/login
3. Get your API key
4. Free tier: 500,000 characters/month

#### LLM API (Choose one or more)

**Option A: OpenAI (Recommended for quality)**
```bash
# Get key from: https://platform.openai.com/
export OPENAI_API_KEY="sk-your-key-here"
```

**Option B: Anthropic (Best for Arabic)**
```bash
# Get key from: https://console.anthropic.com/
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**Option C: Zhipu (Best value)**
```bash
# Get key from: https://open.bigmodel.cn/
export ZHIPU_API_KEY="your-key-here"
```

**Option D: Google Gemini (Balanced)**
```bash
# Get key from: https://aistudio.google.com/
export GOOGLE_API_KEY="your-key-here"
```

### Step 4: Test Connection
```bash
# Test DeepL
npm run test:connection

# Test LLM providers
npm run test:llm
```

### Step 5: Run Translation
```bash
# Translate all languages
npm run translate:v2

# Or translate specific languages
npm run translate:v2 -- --locales=zh-CN,ja,ar
```

## 📊 What You'll Get

After running, you'll see:
```
✅ Translation complete!

📊 Statistics:
  Total: 1092 translations
  Auto-approved: 945 (86.5%)
  Manual review: 147 (13.5%)
  Average score: 0.87/1.0

📁 Generated files:
  - apps/web/src/locales/zh-CN.json
  - apps/web/src/locales/es.json
  - ...
  - translation-quality-report-v2.md
```

## 🎯 Recommended Configurations

### For Development/Testing
```bash
# Cheap and fast
export ZHIPU_API_KEY="..."
npm run translate:v2 -- --locales=zh-CN
```
**Cost**: ~$0.009/translation

### For Production
```bash
# High quality with load balancing
export OPENAI_API_KEY="..."
export ANTHROPIC_API_KEY="..."
export LLM_PROVIDERS="openai,anthropic"
export ENABLE_LOAD_BALANCING=true
npm run translate:v2
```
**Cost**: ~$0.025/translation

### For Arabic Projects
```bash
# Optimized for Arabic RTL
export ANTHROPIC_API_KEY="..."
npm run translate:v2 -- --locales=ar --min-score=0.85
```
**Cost**: ~$0.025/translation

### For Chinese Projects
```bash
# Chinese-optimized
export ZHIPU_API_KEY="..."
export BAIDU_API_KEY="..."
npm run translate:v2 -- --locales=zh-CN,ja,ko
```
**Cost**: ~$0.009/translation

## 📂 File Locations

### Input (Source)
```
# Your English translations
apps/web/src/locales/en.json
```

### Output (Generated)
```
# Translated files
apps/web/src/locales/zh-CN.json
apps/web/src/locales/es.json
apps/web/src/locales/fr.json
...

# Reports
translation-quality-report-v2.md
translation-report-zh-CN.md
translation-report-es.md
...
```

## 🔧 Common Commands

```bash
# View help
npm run translate:v2 -- --help

# Custom quality threshold
npm run translate:v2 -- --min-score=0.9

# Custom batch size
npm run translate:v2 -- --batch-size=30

# Load balancing mode
npm run translate:v2 -- --load-balance

# Combine options
npm run translate:v2 \
  --locales=zh-CN,ja,ar \
  --min-score=0.85 \
  --batch-size=30 \
  --load-balance
```

## 📈 Understanding Quality Scores

- **0.9-1.0**: Excellent (auto-approved)
- **0.7-0.89**: Good (auto-approved)
- **0.5-0.69**: Fair (manual review)
- **0-0.49**: Poor (manual rewrite)

## 🌍 Supported Languages

| Code | Name | Native Name | RTL | Special Features |
|------|------|-------------|-----|------------------|
| en | English | English | ❌ | Source language |
| zh-CN | Chinese Simplified | 简体中文 | ❌ | - |
| es | Spanish | Español | ❌ | - |
| fr | French | Français | ❌ | - |
| de | German | Deutsch | ❌ | - |
| ja | Japanese | 日本語 | ❌ | - |
| ko | Korean | 한국어 | ❌ | - |
| ar | Arabic | العربية | ✅ | RTL, Cultural filters |

## 🛠️ Troubleshooting

### Error: "DEEPL_API_KEY not set"
```bash
# Solution
export DEEPL_API_KEY="your-actual-key"
echo $DEEPL_API_KEY  # Verify
```

### Error: "LLM provider failed"
```bash
# Solution: Try different provider
export OPENAI_API_KEY="..."  # Switch to OpenAI
npm run test:llm  # Test first
```

### Low quality scores (<0.7)
```bash
# Solutions:
1. Use better LLM (Claude/GPT-4)
2. Increase quality threshold
3. Manual review needed
```

### Timeout errors
```bash
# Solutions:
1. Reduce batch size: --batch-size=30
2. Check network connection
3. Verify API limits
```

## 💰 Cost Calculator

### Per 1000 translations:
| Setup | DeepL | LLM | Total | Savings |
|-------|--------|-----|-------|---------|
| Manual | $0 | $5,340 | $5,340 | - |
| Single LLM | $0.50 | $2.50 | $3.00 | 99.9% |
| Load Balanced | $0.50 | $2.50 | $3.00 | 99.9% |

**Note**: LLM cost varies by provider and usage.

## 📚 Next Steps

1. **Review quality report**: `cat translation-quality-report-v2.md`
2. **Fix low-score translations**: Edit files manually
3. **Integrate with HDCP**: Copy files to `apps/web/src/locales/`
4. **Test in browser**: Visit `/zh-CN`, `/ar` pages
5. **Optimize**: Adjust thresholds based on results

## 📖 Documentation

- **Full Guide**: `README.md`
- **LLM Comparison**: `LLM_PROVIDER_GUIDE.md`
- **Configuration**: `QUICK_CONFIG.md`
- **Examples**: `SOLUTION_SUMMARY.md`

## 🎓 Learning Resources

1. **Start here**: `QUICK_CONFIG.md` - 5-minute setup
2. **Choose LLM**: `LLM_PROVIDER_GUIDE.md` - Compare providers
3. **Understand flow**: `FLOWCHART.md` - See how it works
4. **Cost analysis**: `COMPARISON.md` - See savings

## 🆘 Need Help?

- **Quick Start**: This guide (you're here!)
- **Full Documentation**: `README.md`
- **LLM Selection**: `LLM_PROVIDER_GUIDE.md`
- **Configuration**: `QUICK_CONFIG.md`
- **Examples**: `SOLUTION_SUMMARY.md`

## ✅ Success Checklist

- [ ] Node.js 18+ installed
- [ ] Dependencies installed (`npm install`)
- [ ] DeepL API key configured
- [ ] At least one LLM API key configured
- [ ] Connection tests pass (`npm run test:llm`)
- [ ] Translation runs successfully
- [ ] Quality report generated
- [ ] Translation files created
- [ ] Files copied to HDCP platform
- [ ] Tested language switching in browser

## 🎉 You're Ready!

Congratulations! You now have a production-ready auto translation service integrated with HDCP Platform.

**Next**: Check out `README.md` for advanced features and customization options.

---

**Pro Tip**: Start with a single language (e.g., `--locales=zh-CN`) to test before running all languages.
