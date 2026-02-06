/**
 * DeepL API 提供者
 * 官方文档: https://www.deepl.com/docs-api
 */

import axios from 'axios';

const DEEPL_API_URL = 'https://api-free.deepl.com/v2/translate'; // 免费版
// const DEEPL_API_URL = 'https://api.deepl.com/v2/translate'; // 付费版

interface DeepLResponse {
  translations: Array<{
    detected_source_language: string;
    text: string;
  }>;
}

/**
 * 使用 DeepL 翻译文本
 */
export async function translateWithDeepL(
  text: string,
  sourceLang: string,
  targetLang: string
): Promise<string> {
  const apiKey = process.env.DEEPL_API_KEY;

  if (!apiKey) {
    throw new Error('DEEPL_API_KEY 未设置');
  }

  try {
    const response = await axios.post<DeepLResponse>(
      DEEPL_API_URL,
      new URLSearchParams({
        auth_key: apiKey,
        text: text,
        source_lang: sourceLang.toUpperCase(),
        target_lang: targetLang.toUpperCase(),
      }),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        timeout: 30000,
      }
    );

    if (response.data.translations && response.data.translations.length > 0) {
      return response.data.translations[0].text;
    }

    throw new Error('DeepL 返回空结果');
  } catch (error: any) {
    console.error('DeepL 翻译错误:', error.response?.data || error.message);
    throw new Error(`DeepL 翻译失败: ${error.message}`);
  }
}

/**
 * 批量翻译（优化版）
 */
export async function batchTranslateWithDeepL(
  texts: string[],
  sourceLang: string,
  targetLang: string
): Promise<string[]> {
  const apiKey = process.env.DEEPL_API_KEY;

  if (!apiKey) {
    throw new Error('DEEPL_API_KEY 未设置');
  }

  try {
    const response = await axios.post<DeepLResponse>(
      DEEPL_API_URL,
      new URLSearchParams({
        auth_key: apiKey,
        text: texts, // 多个文本
        source_lang: sourceLang.toUpperCase(),
        target_lang: targetLang.toUpperCase(),
      }),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        timeout: 30000,
      }
    );

    return response.data.translations.map(t => t.text);
  } catch (error: any) {
    console.error('DeepL 批量翻译错误:', error.response?.data || error.message);
    throw new Error(`DeepL 批量翻译失败: ${error.message}`);
  }
}

/**
 * 获取支持的语言列表
 */
export async function getDeepLLanguages(): Promise<any> {
  const apiKey = process.env.DEEPL_API_KEY;

  if (!apiKey) {
    throw new Error('DEEPL_API_KEY 未设置');
  }

  try {
    const response = await axios.get('https://api-free.deepl.com/v2/languages', {
      params: {
        auth_key: apiKey,
        type: 'target',
      },
    });

    return response.data;
  } catch (error: any) {
    console.error('获取 DeepL 语言列表错误:', error.message);
    throw error;
  }
}
