#!/usr/bin/env ts-node
/**
 * 测试 API 连接
 */

import axios from 'axios';

async function testDeepLConnection(): Promise<boolean> {
  console.log('🔍 测试 DeepL API 连接...');

  const apiKey = process.env.DEEPL_API_KEY;
  if (!apiKey) {
    console.error('❌ DEEPL_API_KEY 未设置');
    return false;
  }

  try {
    const response = await axios.post(
      'https://api-free.deepl.com/v2/languages',
      new URLSearchParams({
        auth_key: apiKey,
        type: 'target',
      }),
      {
        timeout: 5000,
      }
    );

    console.log('✅ DeepL API 连接成功');
    console.log(`   支持 ${response.data.length} 种目标语言`);
    return true;
  } catch (error: any) {
    console.error('❌ DeepL API 连接失败:', error.message);
    return false;
  }
}

async function testOpenAIConnection(): Promise<boolean> {
  console.log('\n🔍 测试 OpenAI API 连接...');

  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    console.error('❌ OPENAI_API_KEY 未设置');
    return false;
  }

  try {
    const response = await axios.post(
      'https://api.openai.com/v1/chat/completions',
      {
        model: 'gpt-3.5-turbo',
        messages: [
          {
            role: 'user',
            content: 'Hello',
          },
        ],
        max_tokens: 5,
      },
      {
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        timeout: 5000,
      }
    );

    console.log('✅ OpenAI API 连接成功');
    console.log(`   模型: gpt-3.5-turbo`);
    return true;
  } catch (error: any) {
    console.error('❌ OpenAI API 连接失败:', error.message);
    return false;
  }
}

async function testFileSystem(): Promise<boolean> {
  console.log('\n🔍 测试文件系统...');

  try {
    const fs = require('fs');
    const path = require('path');

    const localesDir = path.join(__dirname, '../apps/web/src/locales');

    if (!fs.existsSync(localesDir)) {
      console.log('⚠️  翻译目录不存在，将自动创建');
      fs.mkdirSync(localesDir, { recursive: true });
    }

    const enFile = path.join(localesDir, 'en.json');
    if (fs.existsSync(enFile)) {
      const content = fs.readFileSync(enFile, 'utf-8');
      const data = JSON.parse(content);
      console.log(`✅ 找到英文翻译文件，包含 ${Object.keys(data).length} 个顶级键`);
    } else {
      console.log('⚠️  未找到 en.json 文件');
    }

    return true;
  } catch (error: any) {
    console.error('❌ 文件系统测试失败:', error.message);
    return false;
  }
}

async function main(): Promise<void> {
  console.log('================================');
  console.log('🧪 HDCP 翻译服务连接测试');
  console.log('================================\n');

  const tests = [
    { name: 'DeepL API', fn: testDeepLConnection },
    { name: 'OpenAI API', fn: testOpenAIConnection },
    { name: '文件系统', fn: testFileSystem },
  ];

  const results = await Promise.all(tests.map(t => t.fn()));

  console.log('\n================================');
  console.log('📊 测试结果汇总');
  console.log('================================');

  tests.forEach((test, i) => {
    const status = results[i] ? '✅ 通过' : '❌ 失败';
    console.log(`${test.name}: ${status}`);
  });

  const allPassed = results.every(r => r);

  if (allPassed) {
    console.log('\n🎉 所有测试通过！可以开始翻译了。');
    console.log('\n运行命令:');
    console.log('  npm run translate:quick');
    console.log('\n或手动运行:');
    console.log('  npx ts-node scripts/translation-service.ts');
  } else {
    console.log('\n⚠️  部分测试失败，请检查配置后重试。');
    process.exit(1);
  }
}

main().catch(console.error);
