#!/bin/bash

# HDCP安全扫描脚本
# Security scan script for HDCP Template

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印横幅
echo -e "${BLUE}"
echo "========================================="
echo "  HDCP Security Scanner"
echo "========================================="
echo -e "${NC}"

# 检查工具是否安装
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${YELLOW}[WARNING]${NC} $1 is not installed. Installing..."
        pip install $2
    fi
}

# 1. 安装安全扫描工具
echo -e "${BLUE}[1/6]${NC} Installing security scanning tools..."

check_tool "safety" "safety"
check_tool "bandit" "bandit"
check_tool "semgrep" "semgrep"

echo -e "${GREEN}[DONE]${NC} Security tools installed"

# 2. 运行依赖安全扫描
echo -e "\n${BLUE}[2/6]${NC} Running dependency security scan (Safety)..."
echo "Scanning Python dependencies..."
safety check --json --output safety-report.json || true
safety check || true

if [ -f safety-report.json ]; then
    echo -e "${GREEN}[DONE]${NC} Safety report saved to safety-report.json"
fi

# 3. 运行代码安全扫描 (Bandit)
echo -e "\n${BLUE}[3/6]${NC} Running code security scan (Bandit)..."
echo "Scanning Python code for security issues..."
bandit -r apps/api/app/ -f json -o bandit-report.json || true
bandit -r apps/api/app/ -f txt || true

if [ -f bandit-report.json ]; then
    echo -e "${GREEN}[DONE]${NC} Bandit report saved to bandit-report.json"
fi

# 4. 运行Semgrep扫描
echo -e "\n${BLUE}[4/6]${NC} Running advanced security scan (Semgrep)..."
echo "Running Semgrep security rules..."
semgrep --config=auto apps/api/app/ --json --output=semgrep-report.json || true
semgrep --config=auto apps/api/app/ || true

if [ -f semgrep-report.json ]; then
    echo -e "${GREEN}[DONE]${NC} Semgrep report saved to semgrep-report.json"
fi

# 5. 检查密钥泄露
echo -e "\n${BLUE}[5/6]${NC} Checking for exposed secrets..."
echo "Scanning for exposed API keys and secrets..."

# 创建临时grep模式
cat > /tmp/secret-patterns.txt <<EOF
-----BEGIN RSA PRIVATE KEY-----
-----BEGIN PRIVATE KEY-----
-----BEGIN PGP PRIVATE KEY BLOCK-----
password\s*=\s*['"][^'"]+['"]
api[_-]?key\s*=\s*['"][^'"]+['"]
secret[_-]?key\s*=\s*['"][^'"]+['"]
token\s*=\s*['"][^'"]+['"]
EOF

# 扫描代码
if grep -r -E -f /tmp/secret-patterns.txt apps/api/ 2>/dev/null; then
    echo -e "${RED}[WARNING]${NC} Potential secrets found in code!"
else
    echo -e "${GREEN}[DONE]${NC} No exposed secrets found"
fi

# 清理
rm -f /tmp/secret-patterns.txt

# 6. 生成摘要报告
echo -e "\n${BLUE}[6/6]${NC} Generating summary report..."

cat > security-summary.md <<EOF
# HDCP Security Scan Report

Generated: $(date)

## Summary

- ✅ Dependency Security Scan (Safety)
- ✅ Code Security Scan (Bandit)
- ✅ Advanced Security Scan (Semgrep)
- ✅ Secret Exposure Check

## Reports

1. **Safety Report**: \`safety-report.json\`
2. **Bandit Report**: \`bandit-report.json\`
3. **Semgrep Report**: \`semgrep-report.json\`

## Next Steps

1. Review all reports
2. Fix critical and high-severity issues
3. Run tests to ensure fixes don't break functionality
4. Commit fixes and create a new security scan

## Tools Used

- [Safety](https://pyup.io/safety/) - Dependency vulnerability scanner
- [Bandit](https://bandit.readthedocs.io/) - Python security linter
- [Semgrep](https://semgrep.dev/) - Static analysis tool

EOF

echo -e "${GREEN}[DONE]${NC} Summary report saved to security-summary.md"

# 显示摘要
echo -e "\n${BLUE}=========================================${NC}"
echo -e "${GREEN}Security Scan Complete${NC}"
echo -e "${BLUE}=========================================${NC}"

echo ""
echo "Reports generated:"
echo "  - safety-report.json"
echo "  - bandit-report.json"
echo "  - semgrep-report.json"
echo "  - security-summary.md"
echo ""

echo "To view reports:"
echo "  cat security-summary.md"
echo "  cat bandit-report.json | jq ."
echo ""

echo -e "${GREEN}✓ Security scan completed!${NC}"
