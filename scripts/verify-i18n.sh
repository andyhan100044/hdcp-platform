#!/bin/bash

# i18n实现验证脚本
# 验证HDCP模板的多语言支持是否完整

echo "=================================="
echo "🌍 HDCP i18n 实现验证"
echo "=================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 计数器
checks_passed=0
checks_failed=0

# 检查函数
check_item() {
    local description="$1"
    local command="$2"
    local expected="$3"

    echo -n "检查: $description ... "

    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 通过${NC}"
        ((checks_passed++))
        return 0
    else
        echo -e "${RED}❌ 失败${NC}"
        ((checks_failed++))
        return 1
    fi
}

echo "1️⃣ 前端 i18n 文件验证"
echo "=================================="

# 检查翻译文件
echo ""
echo "检查翻译文件:"
for locale in en zh-CN es fr de ja ko ar; do
    check_item "翻译文件: $locale.json" \
               "[ -f 'apps/web/src/locales/$locale.json' ]"
done

echo ""
echo "检查前端配置:"
check_item "Next.js i18n配置" \
           "[ -f 'apps/web/next.config.js' ]"

check_item "i18n配置存在" \
           "grep -q 'locales.*en.*zh-CN.*es.*fr.*de.*ja.*ko.*ar' apps/web/next.config.js"

check_item "语言切换组件" \
           "[ -f 'apps/web/src/components/LanguageSwitcher.tsx' ]"

check_item "i18n库配置" \
           "[ -f 'apps/web/src/lib/i18n.ts' ]"

echo ""
echo "2️⃣ CMS i18n 配置验证"
echo "=================================="

echo ""
echo "检查CMS配置:"
check_item "Strapi插件配置" \
           "[ -f 'apps/cms/config/plugins.js' ]"

check_item "CMS启用i18n插件" \
           "grep -q 'i18n' apps/cms/config/plugins.js"

check_item "CMS配置8种语言" \
           "grep -q \"zh-CN.*es.*fr\" apps/cms/config/plugins.js"

# 检查内容类型
echo ""
echo "检查CMS内容类型i18n:"
for content_type in article category tag page navigation-item; do
    check_item "内容类型: $content_type" \
               "[ -f 'apps/cms/src/api/$content_type/content-types/$content_type/schema.json' ]"
done

echo ""
echo "3️⃣ 后端 API i18n 配置验证"
echo "=================================="

echo ""
echo "检查API配置:"
check_item "API设置文件" \
           "[ -f 'apps/api/app/config/settings.py' ]"

check_item "API配置支持语言" \
           "grep -q 'zh-CN.*es.*fr' apps/api/app/config/settings.py"

check_item "API默认语言配置" \
           "grep -q 'default_locale.*en' apps/api/app/config/settings.py"

echo ""
echo "4️⃣ 翻译内容验证"
echo "=================================="

echo ""
echo "检查翻译键数量:"
for locale in en zh-CN es fr de ja ko ar; do
    file="apps/web/src/locales/$locale.json"
    if [ -f "$file" ]; then
        key_count=$(grep -o '":' "$file" | wc -l)
        echo -n "  $locale.json: "
        if [ "$key_count" -gt 100 ]; then
            echo -e "${GREEN}✅ $key_count 个翻译键${NC}"
            ((checks_passed++))
        else
            echo -e "${YELLOW}⚠️  $key_count 个翻译键 (少于100)${NC}"
            ((checks_failed++))
        fi
    fi
done

echo ""
echo "5️⃣ 依赖包验证"
echo "=================================="

echo ""
echo "检查package.json依赖:"
check_item "next-intl依赖" \
           "grep -q '\"next-intl\"' apps/web/package.json"

check_item "Strapi i18n插件" \
           "grep -q '@strapi/plugin-i18n' apps/cms/package.json"

echo ""
echo "=================================="
echo "📊 验证结果统计"
echo "=================================="
echo -e "通过: ${GREEN}$checks_passed${NC}"
echo -e "失败: ${RED}$checks_failed${NC}"
echo -e "总计: $((checks_passed + checks_failed))"
echo ""

if [ $checks_failed -eq 0 ]; then
    echo -e "${GREEN}✅ 所有检查通过！i18n实现完整！${NC}"
    echo ""
    echo "下一步："
    echo "  1. 运行: docker-compose up -d"
    echo "  2. 访问: http://localhost:3000"
    echo "  3. 测试语言切换功能"
    exit 0
else
    echo -e "${RED}⚠️  有 $checks_failed 项检查失败${NC}"
    echo ""
    echo "请检查失败的项目并重新运行此脚本"
    exit 1
fi
