#!/usr/bin/env ts-node
/**
 * 测试多个 LLM 提供商
 */

import { LLMManager } from './providers/llm-providers';

async function testProviders(): Promise<void> {
  console.log('🧪 LLM 提供商测试\n');
  console.log('='.repeat(50));

  const manager = new LLMManager();
  const availableProviders = manager.getAvailableProviders();

  console.log(`\n📊 可用提供商: ${availableProviders.length} 个`);
  if (availableProviders.length === 0) {
    console.log('\n❌ 没有配置任何 LLM 提供商');
    console.log('\n💡 请配置至少一个 API 密钥:');
    console.log('   export OPENAI_API_KEY="sk-..."');
    console.log('   export ANTHROPIC_API_KEY="sk-ant-..."');
    console.log('   export ZHIPU_API_KEY="..."');
    return;
  }

  console.log(`✅ 已配置: ${availableProviders.join(', ')}\n`);

  // 测试请求
  const testRequests = [
    {
      sourceText: 'Hello World',
      translation: '你好世界',
      targetLocale: 'zh-CN',
      translationKey: 'test.hello',
    },
    {
      sourceText: 'Save',
      translation: '保存',
      targetLocale: 'zh-CN',
      translationKey: 'common.save',
    },
    {
      sourceText: 'Arabic is written from right to left',
      translation: '阿拉伯语从右向左书写',
      targetLocale: 'zh-CN',
      translationKey: 'test.rtl',
    },
  ];

  console.log('\n🚀 开始测试...\n');

  for (const provider of availableProviders) {
    console.log(`\n${'='.repeat(50)}`);
    console.log(`📌 测试提供商: ${provider.toUpperCase()}`);
    console.log('='.repeat(50));

    let successCount = 0;
    let totalLatency = 0;

    for (const request of testRequests) {
      try {
        console.log(`\n测试: "${request.sourceText}"`);
        console.log(`翻译: "${request.translation}"`);

        const start = Date.now();
        const result = await manager.reviewTranslation(request, provider as any);

        totalLatency += result.latency;
        successCount++;

        console.log(`✅ 成功`);
        console.log(`   改进翻译: ${result.correctedText}`);
        console.log(`   质量评分: ${(result.score * 100).toFixed(1)}/100`);
        console.log(`   响应时间: ${result.latency}ms`);
        if (result.issues.length > 0) {
          console.log(`   问题: ${result.issues.join(', ')}`);
        }
      } catch (error: any) {
        console.log(`❌ 失败: ${error.message}`);
      }
    }

    console.log(`\n📊 ${provider} 总结:`);
    console.log(`   成功率: ${((successCount / testRequests.length) * 100).toFixed(1)}%`);
    console.log(`   平均响应: ${(totalLatency / successCount || 0).toFixed(0)}ms`);
  }

  console.log(`\n${'='.repeat(50)}`);
  console.log('🎉 测试完成！');
  console.log('='.repeat(50));

  // 推荐配置
  console.log('\n💡 推荐配置:');

  if (availableProviders.includes('openai')) {
    console.log('\n  🏆 最佳质量:');
    console.log('     OPENAI_API_KEY=sk-...');
    console.log('     LLM_PROVIDERS=openai');
  }

  if (availableProviders.includes('anthropic')) {
    console.log('\n  🎯 最佳推理:');
    console.log('     ANTHROPIC_API_KEY=sk-ant-...');
    console.log('     LLM_PROVIDERS=anthropic');
  }

  if (availableProviders.includes('zhipu')) {
    console.log('\n  💰 最佳性价比:');
    console.log('     ZHIPU_API_KEY=...');
    console.log('     LLM_PROVIDERS=zhipu');
  }

  if (availableProviders.includes('google')) {
    console.log('\n  ⚡ 最快响应:');
    console.log('     GOOGLE_API_KEY=...');
    console.log('     LLM_PROVIDERS=google');
  }

  if (availableProviders.includes('baidu')) {
    console.log('\n  🇨🇳 中文最佳:');
    console.log('     BAIDU_API_KEY=...');
    console.log('     BAIDU_SECRET_KEY=...');
    console.log('     LLM_PROVIDERS=baidu');
  }

  console.log('\n🚀 负载均衡 (推荐用于生产):');
  console.log('   LLM_PROVIDERS=openai,zhipu,google');
  console.log('   ENABLE_LOAD_BALANCING=true');
  console.log('   npm run translate:v2 -- --load-balance');

  console.log('\n📖 详细指南:');
  console.log('   cat LLM_PROVIDER_GUIDE.md');
}

main().catch(console.error);

async function main() {
  try {
    await testProviders();
  } catch (error: any) {
    console.error('❌ 测试失败:', error);
    process.exit(1);
  }
}
