/**
 * LLM 翻译质量校核提供者
 * 使用 GPT-4 对翻译质量进行评分和改进
 */

import { OpenAI } from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

interface ReviewResult {
  correctedText: string;
  score: number; // 0-1 分
  issues: string[];
  suggestions: string[];
}

/**
 * 使用 LLM 校核翻译质量
 */
export async function reviewWithLLM(
  sourceText: string,
  translation: string,
  targetLocale: string,
  translationKey: string
): Promise<ReviewResult> {
  const localeContext = getLocaleContext(targetLocale);

  const prompt = `
你是一个专业的翻译质量校核员。请对以下翻译进行质量评估和改进：

原文 (${localeContext.sourceLangName}):
"${sourceText}"

翻译 (${localeContext.targetLangName}):
"${translation}"

翻译键: ${translationKey}

请从以下维度评估翻译质量 (1-10分):
1. 准确性 - 翻译是否忠实于原文
2. 流畅性 - 目标语言表达是否自然流畅
3. 文化适配 - 是否符合目标语言文化习惯
4. 术语一致性 - 专业术语翻译是否准确
5. 格式保留 - 是否保留了原文的格式和结构

对于阿拉伯语 (ar)，特别注意:
- 是否使用了正确的 RTL 语言习惯
- 是否避免了文化敏感内容
- 数字是否使用正确的格式
- 是否有语法或拼写错误

请返回 JSON 格式:
{
  "correctedText": "改进后的翻译",
  "score": 0.85,
  "issues": ["问题1", "问题2"],
  "suggestions": ["建议1", "建议2"]
}

评分标准:
- 0.9-1.0: 优秀，无需改进
- 0.7-0.89: 良好，小幅改进
- 0.5-0.69: 一般，需明显改进
- 0-0.49: 差，需重译

请只返回 JSON，不要其他文字。
`;

  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages: [
        {
          role: 'system',
          content: '你是一个专业的翻译质量校核员，负责评估和改进机器翻译的质量。',
        },
        {
          role: 'user',
          content: prompt,
        },
      ],
      temperature: 0.3,
      response_format: { type: 'json_object' },
    });

    const content = response.choices[0].message.content;
    if (!content) {
      throw new Error('LLM 返回空结果');
    }

    const result = JSON.parse(content);
    return {
      correctedText: result.correctedText || translation,
      score: Math.max(0, Math.min(1, result.score || 0)),
      issues: result.issues || [],
      suggestions: result.suggestions || [],
    };
  } catch (error: any) {
    console.error('LLM 校核错误:', error.message);
    return {
      correctedText: translation,
      score: 0.5,
      issues: [`LLM 校核失败: ${error.message}`],
      suggestions: ['请手动检查翻译质量'],
    };
  }
}

/**
 * 批量校核翻译
 */
export async function batchReviewWithLLM(
  translations: Array<{
    source: string;
    text: string;
    locale: string;
    key: string;
  }>
): Promise<ReviewResult[]> {
  const batchSize = 10; // 控制并发数量

  const results: ReviewResult[] = [];

  for (let i = 0; i < translations.length; i += batchSize) {
    const batch = translations.slice(i, i + batchSize);
    console.log(`校核批次 ${Math.floor(i / batchSize) + 1}/${Math.ceil(translations.length / batchSize)}`);

    const batchPromises = batch.map(({ source, text, locale, key }) =>
      reviewWithLLM(source, text, locale, key)
    );

    const batchResults = await Promise.all(batchPromises);
    results.push(...batchResults);

    // 避免 API 速率限制
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  return results;
}

/**
 * 获取语言上下文信息
 */
function getLocaleContext(locale: string): {
  sourceLangName: string;
  targetLangName: string;
} {
  const contexts: Record<string, { sourceLangName: string; targetLangName: string }> = {
    'zh-CN': { sourceLangName: '英文', targetLangName: '简体中文' },
    'es': { sourceLangName: '英文', targetLangName: '西班牙语' },
    'fr': { sourceLangName: '英文', targetLangName: '法语' },
    'de': { sourceLangName: '英文', targetLangName: '德语' },
    'ja': { sourceLangName: '英文', targetLangName: '日语' },
    'ko': { sourceLangName: '英文', targetLangName: '韩语' },
    'ar': { sourceLangName: '英文', targetLangName: '阿拉伯语' },
  };

  return contexts[locale] || { sourceLangName: '英文', targetLangName: locale };
}

/**
 * 生成翻译质量报告
 */
export function generateQualityReport(results: ReviewResult[]): void {
  const total = results.length;
  const excellent = results.filter(r => r.score >= 0.9).length;
  const good = results.filter(r => r.score >= 0.7 && r.score < 0.9).length;
  const average = results.filter(r => r.score >= 0.5 && r.score < 0.7).length;
  const poor = results.filter(r => r.score < 0.5).length;

  const report = `
# 翻译质量报告

## 总体统计
- 总翻译数: ${total}
- 优秀 (≥0.9): ${excellent} (${((excellent / total) * 100).toFixed(1)}%)
- 良好 (0.7-0.89): ${good} (${((good / total) * 100).toFixed(1)}%)
- 一般 (0.5-0.69): ${average} (${((average / total) * 100).toFixed(1)}%)
- 差 (<0.5): ${poor} (${((poor / total) * 100).toFixed(1)}%)

## 需人工审核的翻译
${results
  .filter(r => r.score < 0.7)
  .map(r => `- **评分**: ${r.score.toFixed(2)}\n  **翻译**: ${r.correctedText}\n  **问题**: ${r.issues.join(', ')}\n`)
  .join('\n')}

## 改进建议
${results
  .flatMap(r => r.suggestions)
  .filter((s, i, arr) => arr.indexOf(s) === i) // 去重
  .map(s => `- ${s}`)
  .join('\n')}
`;

  console.log(report);
  writeFileSync('translation-quality-report.md', report);
}
