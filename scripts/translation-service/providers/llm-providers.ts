/**
 * 多 LLM 提供者统一接口
 * 支持 OpenAI、Anthropic、Google、国产大模型等
 */

import { OpenAI } from 'openai';
import axios from 'axios';

// ============ 提供商类型定义 ============
export type LLMProvider = 'openai' | 'anthropic' | 'google' | 'cohere' | 'zhipu' | 'baidu' | 'ali' | 'tencent' | 'moonshot';

interface ReviewRequest {
  sourceText: string;
  translation: string;
  targetLocale: string;
  translationKey: string;
  provider: LLMProvider;
}

interface ReviewResult {
  correctedText: string;
  score: number; // 0-1 分
  issues: string[];
  suggestions: string[];
  provider: string;
  latency: number; // 响应时间 (毫秒)
}

// ============ OpenAI 提供者 ============
class OpenAIProvider {
  private client: OpenAI;

  constructor(apiKey: string) {
    this.client = new OpenAI({ apiKey });
  }

  async review(request: ReviewRequest): Promise<ReviewResult> {
    const prompt = this.buildPrompt(request);
    const start = Date.now();

    try {
      const response = await this.client.chat.completions.create({
        model: 'gpt-4-turbo-preview', // 可配置
        messages: [
          { role: 'system', content: '你是一个专业的翻译质量校核员。' },
          { role: 'user', content: prompt }
        ],
        temperature: 0.3,
        response_format: { type: 'json_object' },
        max_tokens: 1000,
      });

      const content = response.choices[0].message.content;
      const result = JSON.parse(content || '{}');

      return {
        correctedText: result.correctedText || request.translation,
        score: Math.max(0, Math.min(1, result.score || 0)),
        issues: result.issues || [],
        suggestions: result.suggestions || [],
        provider: 'openai',
        latency: Date.now() - start,
      };
    } catch (error: any) {
      throw new Error(`OpenAI 错误: ${error.message}`);
    }
  }

  private buildPrompt(request: ReviewRequest): string {
    const { sourceText, translation, targetLocale, translationKey } = request;
    const localeContext = this.getLocaleContext(targetLocale);

    return `
你是一个翻译质量专家。请评估以下翻译：

原文: "${sourceText}"
翻译: "${translation}"
语言: ${localeContext.targetLangName}
上下文: ${translationKey}

评估标准:
1. 准确性 - 翻译是否忠实于原文
2. 流畅性 - 表达是否自然流畅
3. 文化适配 - 是否符合目标语言文化
4. 术语一致 - 专业术语是否准确
5. 格式保留 - 是否保持原有格式

${localeContext.specialRules}

请返回 JSON:
{
  "correctedText": "改进后的翻译",
  "score": 0.85,
  "issues": ["问题1"],
  "suggestions": ["建议1"]
}
`;
  }

  private getLocaleContext(locale: string): { targetLangName: string; specialRules: string } {
    const contexts: Record<string, { targetLangName: string; specialRules: string }> = {
      'zh-CN': { targetLangName: '简体中文', specialRules: '检查是否使用简体中文（非繁体）。' },
      'es': { targetLangName: '西班牙语', specialRules: '注意区分西班牙西班牙语和拉丁美洲西班牙语。' },
      'fr': { targetLangName: '法语', specialRules: '检查性别、单复数、阴阳性是否正确。' },
      'de': { targetLangName: '德语', specialRules: '注意德语的大小写规则和复合词。' },
      'ja': { targetLangName: '日语', specialRules: '检查敬语使用、假名和汉字混用。' },
      'ko': { targetLangName: '韩语', specialRules: '检查敬语等级是否合适。' },
      'ar': {
        targetLangName: '阿拉伯语',
        specialRules: `⚠️ 阿语特殊检查:
- 必须使用 RTL 语言习惯
- 避免酒精、猪肉、彩虹等文化敏感内容
- 使用正确的数字格式 (0123456789)
- 检查语法和拼写错误`
      },
    };

    return contexts[locale] || { targetLangName: locale, specialRules: '' };
  }
}

// ============ Anthropic Claude 提供者 ============
class AnthropicProvider {
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async review(request: ReviewRequest): Promise<ReviewResult> {
    const prompt = this.buildPrompt(request);
    const start = Date.now();

    try {
      const response = await axios.post(
        'https://api.anthropic.com/v1/messages',
        {
          model: 'claude-3-sonnet-20240229',
          max_tokens: 1000,
          messages: [
            { role: 'user', content: prompt }
          ]
        },
        {
          headers: {
            'x-api-key': this.apiKey,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json',
          },
          timeout: 30000,
        }
      );

      const content = response.data.content[0].text;
      const result = this.parseJSON(content);

      return {
        correctedText: result.correctedText || request.translation,
        score: Math.max(0, Math.min(1, result.score || 0)),
        issues: result.issues || [],
        suggestions: result.suggestions || [],
        provider: 'anthropic',
        latency: Date.now() - start,
      };
    } catch (error: any) {
      throw new Error(`Anthropic 错误: ${error.message}`);
    }
  }

  private buildPrompt(request: ReviewRequest): string {
    // Anthropic Claude 的提示词需要调整
    const { sourceText, translation, targetLocale, translationKey } = request;

    return `
请作为翻译质量专家，评估以下翻译质量。

**任务**: 评估翻译质量并提供改进建议

**原文**: ${sourceText}
**翻译**: ${translation}
**目标语言**: ${targetLocale}
**上下文**: ${translationKey}

**评估维度**:
- 准确性 (1-10分)
- 流畅性 (1-10分)
- 文化适配 (1-10分)
- 术语一致性 (1-10分)
- 格式保留 (1-10分)

**输出格式** (必须是有效 JSON):
{
  "correctedText": "改进后的翻译",
  "score": 0.85,
  "issues": ["问题1", "问题2"],
  "suggestions": ["建议1", "建议2"]
}

请仅返回 JSON，不要其他文字。
`;
  }

  private parseJSON(text: string): any {
    try {
      // Claude 可能返回包含 JSON 的文本，需要提取
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      return jsonMatch ? JSON.parse(jsonMatch[0]) : {};
    } catch {
      return {};
    }
  }
}

// ============ Google Gemini 提供者 ============
class GoogleProvider {
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async review(request: ReviewRequest): Promise<ReviewResult> {
    const prompt = this.buildPrompt(request);
    const start = Date.now();

    try {
      const response = await axios.post(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${this.apiKey}`,
        {
          contents: [{
            parts: [{ text: prompt }]
          }],
          generationConfig: {
            temperature: 0.3,
            maxOutputTokens: 1000,
          }
        },
        {
          headers: { 'content-type': 'application/json' },
          timeout: 30000,
        }
      );

      const content = response.data.candidates[0].content.parts[0].text;
      const result = this.parseJSON(content);

      return {
        correctedText: result.correctedText || request.translation,
        score: Math.max(0, Math.min(1, result.score || 0)),
        issues: result.issues || [],
        suggestions: result.suggestions || [],
        provider: 'google',
        latency: Date.now() - start,
      };
    } catch (error: any) {
      throw new Error(`Google 错误: ${error.message}`);
    }
  }

  private buildPrompt(request: ReviewRequest): string {
    return `
评估翻译质量：

原文: ${request.sourceText}
翻译: ${request.translation}
语言: ${request.targetLocale}

返回 JSON 格式:
{
  "correctedText": "改进翻译",
  "score": 0.85,
  "issues": ["问题"],
  "suggestions": ["建议"]
}
`;
  }

  private parseJSON(text: string): any {
    try {
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      return jsonMatch ? JSON.parse(jsonMatch[0]) : {};
    } catch {
      return {};
    }
  }
}

// ============ 国产大模型 ============

// 智谱 ChatGLM
class ZhipuProvider {
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async review(request: ReviewRequest): Promise<ReviewResult> {
    const prompt = this.buildPrompt(request);
    const start = Date.now();

    try {
      const response = await axios.post(
        'https://open.bigmodel.cn/api/paas/v4/chat/completions',
        {
          model: 'glm-4',
          messages: [
            { role: 'user', content: prompt }
          ],
          temperature: 0.3,
          max_tokens: 1000,
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'content-type': 'application/json',
          },
          timeout: 30000,
        }
      );

      const content = response.data.choices[0].message.content;
      const result = this.parseJSON(content);

      return {
        correctedText: result.correctedText || request.translation,
        score: Math.max(0, Math.min(1, result.score || 0)),
        issues: result.issues || [],
        suggestions: result.suggestions || [],
        provider: 'zhipu',
        latency: Date.now() - start,
      };
    } catch (error: any) {
      throw new Error(`智谱 错误: ${error.message}`);
    }
  }

  private buildPrompt(request: ReviewRequest): string {
    return `
翻译质量评估：

原文: ${request.sourceText}
翻译: ${request.translation}
目标语言: ${request.targetLocale}

请返回 JSON:
{"correctedText": "...", "score": 0.85, "issues": [], "suggestions": []}
`;

  }

  private parseJSON(text: string): any {
    try {
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      return jsonMatch ? JSON.parse(jsonMatch[0]) : {};
    } catch {
      return {};
    }
  }
}

// 百度文心一言
class BaiduProvider {
  private apiKey: string;
  private secretKey: string;
  private accessToken: string = '';

  constructor(apiKey: string, secretKey: string) {
    this.apiKey = apiKey;
    this.secretKey = secretKey;
  }

  private async getAccessToken(): Promise<string> {
    if (this.accessToken) return this.accessToken;

    const response = await axios.post(
      'https://aip.baidubce.com/oauth/2.0/token',
      null,
      {
        params: {
          grant_type: 'client_credentials',
          client_id: this.apiKey,
          client_secret: this.secretKey,
        }
      }
    );

    this.accessToken = response.data.access_token;
    return this.accessToken;
  }

  async review(request: ReviewRequest): Promise<ReviewResult> {
    const token = await this.getAccessToken();
    const prompt = this.buildPrompt(request);
    const start = Date.now();

    try {
      const response = await axios.post(
        `https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-4.0?access_token=${token}`,
        {
          messages: [{ role: 'user', content: prompt }],
          temperature: 0.3,
          max_output_tokens: 1000,
        },
        {
          headers: { 'content-type': 'application/json' },
          timeout: 30000,
        }
      );

      const content = response.data.result;
      const result = this.parseJSON(content);

      return {
        correctedText: result.correctedText || request.translation,
        score: Math.max(0, Math.min(1, result.score || 0)),
        issues: result.issues || [],
        suggestions: result.suggestions || [],
        provider: 'baidu',
        latency: Date.now() - start,
      };
    } catch (error: any) {
      throw new Error(`百度 错误: ${error.message}`);
    }
  }

  private buildPrompt(request: ReviewRequest): string {
    return `评估翻译："${request.sourceText}" -> "${request.translation}" (${request.targetLocale})
返回 JSON: {"correctedText": "...", "score": 0.85}`;
  }

  private parseJSON(text: string): any {
    try {
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      return jsonMatch ? JSON.parse(jsonMatch[0]) : {};
    } catch {
      return {};
    }
  }
}

// 月之暗面 Kimi
class MoonshotProvider {
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async review(request: ReviewRequest): Promise<ReviewResult> {
    const prompt = this.buildPrompt(request);
    const start = Date.now();

    try {
      const response = await axios.post(
        'https://api.moonshot.cn/v1/chat/completions',
        {
          model: 'moonshot-v1-8k',
          messages: [{ role: 'user', content: prompt }],
          temperature: 0.3,
          max_tokens: 1000,
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'content-type': 'application/json',
          },
          timeout: 30000,
        }
      );

      const content = response.data.choices[0].message.content;
      const result = this.parseJSON(content);

      return {
        correctedText: result.correctedText || request.translation,
        score: Math.max(0, Math.min(1, result.score || 0)),
        issues: result.issues || [],
        suggestions: result.suggestions || [],
        provider: 'moonshot',
        latency: Date.now() - start,
      };
    } catch (error: any) {
      throw new Error(`月之暗面 错误: ${error.message}`);
    }
  }

  private buildPrompt(request: ReviewRequest): string {
    return `翻译质量评估:
原文: ${request.sourceText}
翻译: ${request.translation}
目标语言: ${request.targetLocale}

JSON 响应: {"correctedText": "...", "score": 0.85}`;
  }

  private parseJSON(text: string): any {
    try {
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      return jsonMatch ? JSON.parse(jsonMatch[0]) : {};
    } catch {
      return {};
    }
  }
}

// ============ LLM 管理器 ============
export class LLMManager {
  private providers: Map<LLMProvider, any> = new Map();

  constructor() {
    this.initializeProviders();
  }

  private initializeProviders() {
    // OpenAI
    if (process.env.OPENAI_API_KEY) {
      this.providers.set('openai', new OpenAIProvider(process.env.OPENAI_API_KEY));
    }

    // Anthropic
    if (process.env.ANTHROPIC_API_KEY) {
      this.providers.set('anthropic', new AnthropicProvider(process.env.ANTHROPIC_API_KEY));
    }

    // Google
    if (process.env.GOOGLE_API_KEY) {
      this.providers.set('google', new GoogleProvider(process.env.GOOGLE_API_KEY));
    }

    // 智谱
    if (process.env.ZHIPU_API_KEY) {
      this.providers.set('zhipu', new ZhipuProvider(process.env.ZHIPU_API_KEY));
    }

    // 百度
    if (process.env.BAIDU_API_KEY && process.env.BAIDU_SECRET_KEY) {
      this.providers.set('baidu', new BaiduProvider(
        process.env.BAIDU_API_KEY,
        process.env.BAIDU_SECRET_KEY
      ));
    }

    // 月之暗面
    if (process.env.MOONSHOT_API_KEY) {
      this.providers.set('moonshot', new MoonshotProvider(process.env.MOONSHOT_API_KEY));
    }
  }

  /**
   * 获取可用的提供商
   */
  getAvailableProviders(): LLMProvider[] {
    return Array.from(this.providers.keys());
  }

  /**
   * 校核翻译
   */
  async reviewTranslation(
    request: Omit<ReviewRequest, 'provider'>,
    preferredProvider?: LLMProvider
  ): Promise<ReviewResult> {
    let provider: LLMProvider;

    if (preferredProvider && this.providers.has(preferredProvider)) {
      provider = preferredProvider;
    } else {
      // 默认使用第一个可用的提供商
      const available = this.getAvailableProviders();
      if (available.length === 0) {
        throw new Error('没有可用的 LLM 提供商');
      }
      provider = available[0];
    }

    const llm = this.providers.get(provider);
    return await llm.review({ ...request, provider });
  }

  /**
   * 批量校核 (使用多个提供商负载均衡)
   */
  async batchReview(
    requests: Omit<ReviewRequest, 'provider'>[],
    providers: LLMProvider[]
  ): Promise<ReviewResult[]> {
    const results: ReviewResult[] = [];
    const providerPool = [...providers];

    for (let i = 0; i < requests.length; i++) {
      const provider = providerPool[i % providerPool.length];
      try {
        const result = await this.reviewTranslation(requests[i], provider);
        results.push(result);
      } catch (error) {
        console.error(`提供商 ${provider} 失败，使用备用提供商:`, error);
        // 使用第一个可用的备用提供商
        const fallback = this.getAvailableProviders()[0];
        const result = await this.reviewTranslation(requests[i], fallback);
        results.push(result);
      }
    }

    return results;
  }
}

// ============ 使用示例 ============
/*
const manager = new LLMManager();

// 获取可用提供商
const providers = manager.getAvailableProviders();
console.log('可用提供商:', providers);

// 单个校核
const result = await manager.reviewTranslation({
  sourceText: 'Hello',
  translation: '你好',
  targetLocale: 'zh-CN',
  translationKey: 'greeting.hello'
}, 'openai');  // 指定提供商

// 批量校核 (负载均衡)
const results = await manager.batchReview([
  { sourceText: 'Hello', translation: '你好', targetLocale: 'zh-CN', translationKey: '1' },
  { sourceText: 'World', translation: '世界', targetLocale: 'zh-CN', translationKey: '2' },
], ['openai', 'anthropic']);  // 轮询使用多个提供商
*/
