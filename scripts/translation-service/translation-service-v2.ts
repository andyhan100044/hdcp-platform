#!/usr/bin/env ts-node
/**
 * 多 LLM 提供者翻译服务 v2.0
 * 支持 OpenAI、Anthropic、智谱、百度等多个 LLM
 */

import axios from 'axios';
import { writeFileSync, readFileSync, existsSync } from 'fs';
import { translateWithDeepL } from './providers/deepl';
import { LLMManager } from './providers/llm-providers';
import { TranslationBatch, TranslationResult } from './types';

// ============ 配置 ============
interface Config {
  sourceLocale: string;
  targetLocales: string[];
  outputDir: string;
  minScore: number;
  batchSize: number;
  maxRetries: number;
  delayBetweenBatches: number;
  llmProviders: string[];
  enableLoadBalancing: boolean;
}

const config: Config = {
  sourceLocale: 'en',
  targetLocales: ['zh-CN', 'es', 'fr', 'de', 'ja', 'ko', 'ar'],
  outputDir: 'apps/web/src/locales',
  minScore: 0.8,
  batchSize: 50,
  maxRetries: 3,
  delayBetweenBatches: 1000,
  // 从环境变量读取，或使用默认
  llmProviders: (process.env.LLM_PROVIDERS || 'openai').split(','),
  enableLoadBalancing: process.env.ENABLE_LOAD_BALANCING === 'true',
};

class TranslationServiceV2 {
  private llmManager: LLMManager;
  private sourceTexts: Record<string, string> = {};

  constructor() {
    this.llmManager = new LLMManager();
  }

  /**
   * 从现有翻译文件提取英文原文
   */
  extractEnglishSource(): Record<string, string> {
    const enFile = `${config.outputDir}/en.json`;
    if (!existsSync(enFile)) {
      throw new Error(`未找到英文原文文件: ${enFile}`);
    }

    const translations = JSON.parse(readFileSync(enFile, 'utf-8'));

    const flatten = (obj: any, prefix = ''): Record<string, string> => {
      let result: Record<string, string> = {};
      for (const [key, value] of Object.entries(obj)) {
        const newKey = prefix ? `${prefix}.${key}` : key;
        if (typeof value === 'string') {
          result[newKey] = value;
        } else if (typeof value === 'object' && value !== null) {
          result = { ...result, ...flatten(value, newKey) };
        }
      }
      return result;
    };

    return flatten(translations);
  }

  /**
   * 检查环境变量
   */
  checkEnvironment(): void {
    const required = ['DEEPL_API_KEY'];
    const missing = required.filter(key => !process.env[key]);

    if (missing.length > 0) {
      throw new Error(`缺少环境变量: ${missing.join(', ')}`);
    }

    // 检查 LLM 提供商
    const availableProviders = this.llmManager.getAvailableProviders();
    if (availableProviders.length === 0) {
      console.warn('⚠️  警告: 没有可用的 LLM 提供商，将跳过质量校核');
    } else {
      console.log(`✅ 已配置 LLM 提供商: ${availableProviders.join(', ')}`);
    }
  }

  /**
   * 批量翻译到单个语言
   */
  async translateToLocale(
    locale: string,
    sourceTexts: Record<string, string>
  ): Promise<TranslationResult[]> {
    console.log(`\n🔄 开始翻译到 ${locale}...`);
    console.log(`📊 源文本数量: ${Object.keys(sourceTexts).length}`);

    const results: TranslationResult[] = [];
    const entries = Object.entries(sourceTexts);

    // 分批处理
    const totalBatches = Math.ceil(entries.length / config.batchSize);
    for (let i = 0; i < entries.length; i += config.batchSize) {
      const batch = entries.slice(i, i + config.batchSize);
      const batchNum = Math.floor(i / config.batchSize) + 1;

      console.log(`\n处理批次 ${batchNum}/${totalBatches} (${batch.length} 项)`);

      const batchPromises = batch.map(async ([key, text]) => {
        let attempts = 0;
        let lastError: Error | null = null;

        while (attempts < config.maxRetries) {
          try {
            // 1. DeepL 翻译
            const deeplTranslation = await translateWithDeepL(
              text,
              config.sourceLocale,
              locale
            );

            // 2. LLM 质量校核 (如果可用)
            let finalTranslation = deeplTranslation;
            let score = 1.0;
            let issues: string[] = [];
            let suggestions: string[] = [];
            let provider = 'deepl-only';

            const availableProviders = this.llmManager.getAvailableProviders();
            if (availableProviders.length > 0) {
              // 选择提供商 (轮询或负载均衡)
              let providerName: string;
              if (config.enableLoadBalancing) {
                const providerIndex = (batchNum - 1) % availableProviders.length;
                providerName = availableProviders[providerIndex];
              } else {
                providerName = config.llmProviders[0] || availableProviders[0];
              }

              try {
                const reviewResult = await this.llmManager.reviewTranslation(
                  {
                    sourceText: text,
                    translation: deeplTranslation,
                    targetLocale: locale,
                    translationKey: key,
                  },
                  providerName as any
                );

                finalTranslation = reviewResult.correctedText;
                score = reviewResult.score;
                issues = reviewResult.issues;
                suggestions = reviewResult.suggestions;
                provider = `deepl+${reviewResult.provider}`;
              } catch (llmError: any) {
                console.warn(`⚠️  LLM 校核失败 (${providerName}):`, llmError.message);
                // 使用 DeepL 原始翻译
                finalTranslation = deeplTranslation;
                score = 0.7; // 默认中等分数
                issues = [`LLM 校核失败: ${llmError.message}`];
                suggestions = ['建议检查 LLM API 配置'];
                provider = 'deepl-only';
              }
            }

            return {
              key,
              source: text,
              translation: finalTranslation,
              originalTranslation: deeplTranslation,
              score,
              issues,
              suggestions,
              approved: score >= config.minScore,
              provider,
            };
          } catch (error: any) {
            attempts++;
            lastError = error;
            console.warn(`⚠️  翻译失败 (尝试 ${attempts}/${config.maxRetries}):`, error.message);

            if (attempts < config.maxRetries) {
              await new Promise(resolve => setTimeout(resolve, 1000 * attempts));
            }
          }
        }

        // 所有重试都失败
        console.error(`❌ 翻译彻底失败: ${key}`);
        return {
          key,
          source: text,
          translation: text, // 回退到原文
          originalTranslation: '',
          score: 0,
          issues: [`翻译错误: ${lastError?.message}`],
          suggestions: ['请手动翻译'],
          approved: false,
          provider: 'failed',
        };
      });

      const batchResults = await Promise.all(batchPromises);
      results.push(...batchResults);

      // 进度统计
      const approvedCount = batchResults.filter(r => r.approved).length;
      const averageScore = batchResults.reduce((sum, r) => sum + r.score, 0) / batchResults.length;
      console.log(`✅ 批次完成: ${approvedCount}/${batchResults.length} 通过, 平均分: ${averageScore.toFixed(2)}`);

      // 延迟避免 API 限制
      if (i + config.batchSize < entries.length) {
        await new Promise(resolve => setTimeout(resolve, config.delayBetweenBatches));
      }
    }

    return results;
  }

  /**
   * 生成翻译文件
   */
  generateTranslationFile(
    results: TranslationResult[],
    locale: string
  ): Record<string, any> {
    const translationObj: Record<string, any> = {};

    results.forEach(({ key, translation }) => {
      const parts = key.split('.');
      let current = translationObj;

      for (let i = 0; i < parts.length - 1; i++) {
        if (!current[parts[i]]) {
          current[parts[i]] = {};
        }
        current = current[parts[i]];
      }

      current[parts[parts.length - 1]] = translation;
    });

    return translationObj;
  }

  /**
   * 生成翻译报告
   */
  generateReport(
    locale: string,
    results: TranslationResult[]
  ): string {
    const total = results.length;
    const approved = results.filter(r => r.approved).length;
    const failed = total - approved;
    const averageScore = total > 0 ? results.reduce((sum, r) => sum + r.score, 0) / total : 0;

    // 统计提供商使用情况
    const providerStats: Record<string, number> = {};
    results.forEach(r => {
      providerStats[r.provider] = (providerStats[r.provider] || 0) + 1;
    });

    // 找出需人工审核的翻译
    const failedTranslations = results
      .filter(r => !r.approved)
      .sort((a, b) => a.score - b.score) // 按分数排序，最差的在前
      .slice(0, 20); // 只显示前 20 个

    return `
================================
翻译报告 - ${locale}
================================
总计翻译: ${total}
自动通过: ${approved} (${((approved / total) * 100).toFixed(1)}%)
失败/需人工: ${failed} (${((failed / total) * 100).toFixed(1)}%)
平均分: ${averageScore.toFixed(2)}/1.0

提供商使用统计:
${Object.entries(providerStats)
  .map(([provider, count]) => `  ${provider}: ${count} (${((count / total) * 100).toFixed(1)}%)`)
  .join('\n')}

需人工审核的翻译 (前 20 个):
${failedTranslations
  .map(r => `  • ${r.key}: ${r.translation} [评分: ${r.score.toFixed(2)}]`)
  .join('\n')}

问题统计:
${this.getIssueStats(results)}

================================
`;
  }

  /**
   * 获取问题统计
   */
  private getIssueStats(results: TranslationResult[]): string {
    const allIssues = results.flatMap(r => r.issues);
    const issueCounts: Record<string, number> = {};

    allIssues.forEach(issue => {
      const key = issue.split(':')[0]; // 取问题类型
      issueCounts[key] = (issueCounts[key] || 0) + 1;
    });

    return Object.entries(issueCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10) // 只显示前 10 个问题
      .map(([issue, count]) => `  ${issue}: ${count} 次`)
      .join('\n');
  }

  /**
   * 生成总体质量报告
   */
  generateQualityReport(allResults: Record<string, TranslationResult[]>): void {
    let totalTranslations = 0;
    let totalApproved = 0;
    const localeStats: Record<string, { total: number; approved: number; avgScore: number }> = {};

    for (const [locale, results] of Object.entries(allResults)) {
      const total = results.length;
      const approved = results.filter(r => r.approved).length;
      const avgScore = results.reduce((sum, r) => sum + r.score, 0) / total;

      localeStats[locale] = {
        total,
        approved,
        avgScore,
      };

      totalTranslations += total;
      totalApproved += approved;
    }

    const overallApproval = (totalApproved / totalTranslations) * 100;

    const report = `
# 多语言翻译质量报告

## 总体统计
- 总翻译数: ${totalTranslations}
- 自动通过: ${totalApproved} (${overallApproval.toFixed(1)}%)
- 需人工: ${totalTranslations - totalApproved} (${(100 - overallApproval).toFixed(1)}%)

## 各语言详情
| 语言 | 总数 | 通过 | 失败 | 通过率 | 平均分 |
|------|------|------|------|--------|--------|
${Object.entries(localeStats)
  .map(([locale, stats]) => {
    const rate = (stats.approved / stats.total) * 100;
    return `| ${locale} | ${stats.total} | ${stats.approved} | ${stats.total - stats.approved} | ${rate.toFixed(1)}% | ${stats.avgScore.toFixed(2)} |`;
  })
  .join('\n')}

## 建议
${overallApproval >= 90 ? '✅ 翻译质量优秀，无需大规模人工审核' : overallApproval >= 80 ? '⚠️ 翻译质量良好，建议人工审核低分翻译' : '❌ 翻译质量一般，需加强人工审核'}

## 配置信息
- LLM 提供商: ${this.llmManager.getAvailableProviders().join(', ') || '无'}
- 质量阈值: ${config.minScore}
${config.enableLoadBalancing ? '- 负载均衡: 已启用' : '- 负载均衡: 未启用'}
`;

    console.log(report);
    writeFileSync('translation-quality-report-v2.md', report);
  }

  /**
   * 运行完整翻译流程
   */
  async run(): Promise<void> {
    try {
      console.log('🚀 多 LLM 提供者翻译服务 v2.0 启动\n');

      // 1. 检查环境
      this.checkEnvironment();
      console.log('✅ 环境检查通过\n');

      // 2. 提取英文原文
      console.log('📝 提取英文原文...');
      this.sourceTexts = this.extractEnglishSource();
      console.log(`✅ 提取到 ${Object.keys(this.sourceTexts).length} 个翻译键\n`);

      // 3. 翻译每种语言
      const allResults: Record<string, TranslationResult[]> = {};

      for (const locale of config.targetLocales) {
        try {
          const results = await this.translateToLocale(locale, this.sourceTexts);
          allResults[locale] = results;

          // 保存翻译文件
          const translationFile = this.generateTranslationFile(results, locale);
          const outputFile = `${config.outputDir}/${locale}.json`;
          writeFileSync(outputFile, JSON.stringify(translationFile, null, 2));
          console.log(`💾 已保存: ${outputFile}\n`);

          // 生成报告
          const report = this.generateReport(locale, results);
          const reportFile = `translation-report-${locale}.md`;
          writeFileSync(reportFile, report);
          console.log(`📄 已生成报告: ${reportFile}\n`);

        } catch (error: any) {
          console.error(`❌ ${locale} 翻译失败:`, error);
        }
      }

      // 4. 生成总体质量报告
      this.generateQualityReport(allResults);
      console.log('📄 已生成总体报告: translation-quality-report-v2.md\n');

      console.log('🎉 所有翻译完成！\n');

      // 5. 输出统计信息
      const totalTranslations = Object.values(allResults).reduce((sum, r) => sum + r.length, 0);
      const totalApproved = Object.values(allResults).reduce((sum, r) => sum + r.filter(x => x.approved).length, 0);
      console.log('📊 最终统计:');
      console.log(`  总翻译: ${totalTranslations}`);
      console.log(`  自动通过: ${totalApproved} (${((totalApproved / totalTranslations) * 100).toFixed(1)}%)`);
      console.log(`  需人工: ${totalTranslations - totalApproved} (${(((totalTranslations - totalApproved) / totalTranslations) * 100).toFixed(1)}%)`);

    } catch (error: any) {
      console.error('❌ 翻译流程失败:', error);
      process.exit(1);
    }
  }
}

// ============ CLI 解析 ============
function parseArgs(): void {
  const args = process.argv.slice(2);

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    switch (arg) {
      case '--locales':
        const locales = args[i + 1];
        if (locales) {
          config.targetLocales = locales.split(',');
          console.log(`📌 已设置目标语言: ${config.targetLocales.join(', ')}`);
        }
        break;

      case '--min-score':
        const score = parseFloat(args[i + 1]);
        if (!isNaN(score)) {
          config.minScore = score;
          console.log(`📌 已设置质量阈值: ${config.minScore}`);
        }
        break;

      case '--batch-size':
        const size = parseInt(args[i + 1]);
        if (!isNaN(size)) {
          config.batchSize = size;
          console.log(`📌 已设置批处理大小: ${config.batchSize}`);
        }
        break;

      case '--llm-providers':
        const providers = args[i + 1];
        if (providers) {
          config.llmProviders = providers.split(',');
          console.log(`📌 已设置 LLM 提供商: ${config.llmProviders.join(', ')}`);
        }
        break;

      case '--load-balance':
        config.enableLoadBalancing = true;
        console.log('📌 已启用负载均衡');
        break;

      case '--help':
        console.log(`
多 LLM 提供者翻译服务 v2.0

选项:
  --locales <list>        目标语言列表 (逗号分隔)
  --min-score <score>    最小通过分数 (0-1)
  --batch-size <size>    批处理大小
  --llm-providers <list> LLM 提供商列表 (逗号分隔)
  --load-balance         启用负载均衡
  --help                 显示此帮助

示例:
  npm run translate:v2 -- --locales=zh-CN,ja --min-score=0.9
  npm run translate:v2 -- --load-balance --llm-providers=openai,zhipu
`);
        process.exit(0);
    }
  }
}

// ============ 主函数 ============
async function main(): Promise<void> {
  parseArgs();
  const service = new TranslationServiceV2();
  await service.run();
}

if (require.main === module) {
  main().catch(console.error);
}

export { TranslationServiceV2 };
