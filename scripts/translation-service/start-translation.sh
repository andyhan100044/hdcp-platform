#!/bin/bash

# 自动翻译服务快速启动脚本

echo "🌍 HDCP 自动翻译服务"
echo "===================="
echo ""

# 检查环境变量
if [ -z "$DEEPL_API_KEY" ]; then
    echo "❌ 错误: DEEPL_API_KEY 未设置"
    echo ""
    echo "请运行:"
    echo "export DEEPL_API_KEY='your-deepl-api-key'"
    echo ""
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ 错误: OPENAI_API_KEY 未设置"
    echo ""
    echo "请运行:"
    echo "export OPENAI_API_KEY='your-openai-api-key'"
    echo ""
    exit 1
fi

echo "✅ 环境变量检查通过"
echo ""

# 确认翻译范围
echo "请选择翻译范围:"
echo "1) 全部语言 (zh-CN, es, fr, de, ja, ko, ar)"
echo "2) 仅亚洲语言 (zh-CN, ja, ko)"
echo "3) 仅欧洲语言 (es, fr, de)"
echo "4) 自定义语言"
echo ""
read -p "请输入选择 (1-4): " choice

case $choice in
    1)
        echo "🌐 翻译全部 7 种语言..."
        export TARGET_LOCALES="zh-CN,es,fr,de,ja,ko,ar"
        ;;
    2)
        echo "🌏 翻译亚洲语言..."
        export TARGET_LOCALES="zh-CN,ja,ko"
        ;;
    3)
        echo "🇪🇺 翻译欧洲语言..."
        export TARGET_LOCALES="es,fr,de"
        ;;
    4)
        echo ""
        read -p "请输入语言代码 (逗号分隔, 例: zh-CN,ja,ar): " custom_locales
        export TARGET_LOCALES="$custom_locales"
        echo "✅ 已设置自定义语言: $TARGET_LOCALES"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "开始翻译..."
echo "===================="
echo ""

# 运行翻译服务
npx ts-node scripts/translation-service.ts

echo ""
echo "===================="
echo "✅ 翻译完成！"
echo ""
echo "📁 生成的文件:"
echo "  - apps/web/src/locales/*.json"
echo "  - translation-report-*.md"
echo "  - translation-quality-report.md"
echo ""
echo "💡 下一步:"
echo "  1. 检查翻译质量报告"
echo "  2. 手动审核评分较低的翻译"
echo "  3. 提交更改到版本控制"
echo ""
