/**
 * 翻译服务类型定义
 */

export interface TranslationBatch {
  locale: string;
  keys: Record<string, string>; // { 'key.path': 'text' }
}

export interface TranslationResult {
  key: string;
  source: string;
  translation: string;
  originalTranslation: string;
  score: number;
  issues: string[];
  suggestions: string[];
  approved: boolean;
}

export interface TranslationConfig {
  sourceLocale: string;
  targetLocales: string[];
  outputDir: string;
  minScore: number;
  batchSize: number;
}

export interface LocaleInfo {
  code: string;
  name: string;
  nativeName: string;
  flag: string;
  rtl: boolean;
  dateFormat: string;
  currency: string;
}

export interface QualityReport {
  locale: string;
  total: number;
  approved: number;
  averageScore: number;
  failedTranslations: TranslationResult[];
}
