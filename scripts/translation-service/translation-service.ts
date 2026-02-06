#!/usr/bin/env ts-node
/**
 * 自动翻译服务
 * 集成 DeepL API + LLM 校核
 */

import axios from 'axios';
import { writeFileSync, readFileSync } from 'fs';
import { translateWithDeepL } from './providers/deepl';
import { reviewWithLLM } from './providers/llm-reviewer';
import { TranslationBatch, TranslationResult } from './types';

const DEEPL_API_KEY = process.env.DEEPL_API_KEY || '';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || '';

class TranslationService {
  private sourceLocale = 'en';
  private targetLocales = ['zh-CN', 'es', 'fr', 'de', 'ja', 'ko', 'ar'];

  /**
   * 从现有翻译文件提取英文原文
   */
  extractEnglishSource(): Record<string, string> {
    const translations = JSON.parse(
      readFileSync('apps/web/src/locales/en.json', 'utf-8')
    );

    // 递归提取所有翻译键
    const flatten = (obj: any, prefix = ''): Record<string, string> => {
      let result: Record<string, string> = {};
      for (const [key, value] of Object.entries(obj)) {
        const newKey = prefix ? `${prefix}.${key}` : key;
        if (typeof value === 'string') {
          result[newKey] = value;
        } else if (typeof value === 'object') {
          result = { ...result, ...flatten(value, newKey) };
        }
      }
      return result;
    };

    return flatten(translations);
  }

  /**
   * 批量翻译
   */
  async batchTranslate(
    sourceTexts: Record<string, string>,
    locale: string
  ): Promise<TranslationResult[]> {
    console.log(`\n🔄 开始翻译到 ${locale}...`);

    const results: TranslationResult[] = [];
    const entries = Object.entries(sourceTexts);

    // 分批处理（避免API限制）
    const batchSize = 50;
    for (let i = 0; i < entries.length; i += batchSize) {
      const batch = entries.slice(i, i + batchSize);
      console.log(`处理批次 ${Math.floor(i / batchSize) + 1}/${Math.ceil(entries.length / batchSize)}`);

      const batchPromises = batch.map(async ([key, text]) => {
        try {
          // 1. DeepL 翻译
          const deeplTranslation = await translateWithDeepL(
            text,
            this.sourceLocale,
            locale
          );

          // 2. LLM 校核
          const reviewResult = await reviewWithLLM(
            text,
            deeplTranslation,
            locale,
            key
          );

          return {
            key,
            source: text,
            translation: reviewResult.correctedText,
            originalTranslation: deeplTranslation,
            score: reviewResult.score,
            issues: reviewResult.issues,
            approved: reviewResult.score >= 0.8, // 80分及以上自动通过
          };
        } catch (error) {
          console.error(`翻译失败 ${key}:`, error);
          return {
            key,
            source: text,
            translation: text, // 回退到原文
            originalTranslation: '',
            score: 0,
            issues: [`翻译错误: ${error}`],
            approved: false,
          };
        }
      });

      const batchResults = await Promise.all(batchPromises);
      results.push(...batchResults);

      // API 速率限制延迟
      await new Promise(resolve => setTimeout(resolve, 1000));
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
      // 将点分隔键转换为嵌套对象
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
  ): void {
    const total = results.length;
    const approved = results.filter(r => r.approved).length;
    const averageScore = results.reduce((sum, r) => sum + r.score, 0) / total;

    const report = `
================================
翻译报告 - ${locale}
================================
总计翻译: ${total}
自动通过: ${approved}
失败/需人工: ${total - approved}
平均分: ${averageScore.toFixed(2)}/1.0

需人工审核的翻译:
${results
  .filter(r => !r.approved)
  .map(r => `- ${r.key}: ${r.translation} (分: ${r.score.toFixed(2)})`)
  .join('\n')}

问题列表:
${results
  .flatMap(r => r.issues.map(issue => `- ${r.key}: ${issue}`))
  .join('\n')}
`;

    console.log(report);
    writeFileSync(`translation-report-${locale}.md`, report);
  }

  /**
   * 运行完整翻译流程
   */
  async run(): Promise<void> {
    if (!DEEPL_API_KEY || !OPENAI_API_KEY) {
      console.error('❌ 请设置 DEEPL_API_KEY 和 OPENAI_API_KEY 环境变量');
      process.exit(1);
    }

    console.log('🚀 开始自动翻译流程...\n');
    console.log('📝 提取英文原文...');

    const sourceTexts = this.extractEnglishSource();
    console.log(`✅ 提取到 ${Object.keys(sourceTexts).length} 个翻译键\n`);

    for (const locale of this.targetLocales) {
      try {
        const results = await this.batchTranslate(sourceTexts, locale);
        const translationFile = this.generateTranslationFile(results, locale);

        // 保存翻译文件
        writeFileSync(
          `apps/web/src/locales/${locale}.json`,
          JSON.stringify(translationFile, null, 2)
        );

        // 生成报告
        this.generateReport(locale, results);

        console.log(`✅ ${locale} 翻译完成并保存\n`);
      } catch (error) {
        console.error(`❌ ${locale} 翻译失败:`, error);
      }
    }

    console.log('🎉 所有翻译完成！');
  }
}

// 运行
const service = new TranslationService();
service.run().catch(console.error);
