# 🗄️ 数据库迁移指南

本指南说明如何在HDCP模板中使用Alembic进行数据库迁移。

---

## 📋 概述

HDCP模板使用**Alembic**作为数据库迁移工具，它允许您：

- 版本控制数据库架构
- 升级/降级数据库
- 与团队协作开发
- 安全地部署变更

---

## 🚀 快速开始

### 自动迁移（推荐）

当您启动Docker Compose时，迁移会自动运行：

```bash
docker-compose up -d
```

迁移服务会在API服务启动之前自动运行，确保数据库始终是最新的。

### 手动迁移

如果您需要手动运行迁移：

```bash
# 进入API容器
docker-compose exec api bash

# 运行迁移
alembic upgrade head

# 查看迁移状态
alembic current
alembic history
```

---

## 📝 创建新迁移

### 方法1: 自动生成迁移

如果您修改了模型（添加新表、列等）：

```bash
# 进入API容器
docker-compose exec api bash

# 生成迁移（基于模型变更）
alembic revision --autogenerate -m "描述您的变更"

# 手动编辑生成的迁移文件
# 文件位于: apps/api/migrations/versions/
```

### 方法2: 手动创建迁移

```bash
# 创建空迁移文件
alembic revision -m "描述您的变更"

# 手动编辑文件添加 SQL
```

---

## 🔧 常用命令

### 查看迁移状态
```bash
# 查看当前版本
alembic current

# 查看迁移历史
alembic history

# 查看详细信息
alembic show HEAD
```

### 升级数据库
```bash
# 升级到最新版本
alembic upgrade head

# 升级到指定版本
alembic upgrade <revision_id>
```

### 降级数据库
```bash
# 降级一个版本
alembic downgrade -1

# 降级到指定版本
alembic downgrade <revision_id>

# 降级到初始状态
alembic downgrade base
```

### 生成SQL
```bash
# 查看迁移SQL（不执行）
alembic upgrade --sql head

# 生成特定迁移的SQL
alembic upgrade --sql <revision_id>
```

---

## 📁 文件结构

```
apps/api/
├── migrations/
│   ├── versions/           # 迁移脚本
│   │   ├── 20260204_1231_46_03f97757c4c1_initial_migration.py
│   │   └── ...
│   ├── env.py            # Alembic环境配置
│   ├── script.py.mako   # 迁移脚本模板
│   └── __init__.py
├── alembic.ini           # Alembic配置文件
└── app/
    ├── models/          # 数据模型
    ├── schemas/         # Pydantic模式
    └── ...
```

---

## 🔍 配置说明

### alembic.ini

主要配置项：

```ini
[alembic]
script_location = migrations          # 迁移脚本位置
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(second).2d_%%(rev)s_%%(slug)s  # 文件名格式

sqlalchemy.url = postgresql+asyncpg://hdcp_user:hdcp_password@postgres:5432/hdcp_db  # 数据库URL
```

### 环境变量

可以通过环境变量覆盖配置：

```bash
# 设置数据库URL
export DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db"

# 运行迁移
alembic upgrade head
```

---

## 💡 最佳实践

### 1. 迁移命名

使用描述性的迁移名称：

```bash
# 好的命名
alembic revision --autogenerate -m "Add user table with email and password"

# 避免模糊命名
alembic revision --autogenerate -m "Add stuff"
```

### 2. 迁移测试

在提交迁移之前，务必测试：

```bash
# 升级到最新版本
alembic upgrade head

# 降级到初始状态
alembic downgrade base

# 再次升级
alembic upgrade head
```

### 3. 数据迁移

对于包含数据的迁移：

```python
def upgrade() -> None:
    # 创建新列
    op.add_column('users', sa.Column('email', sa.String(255)))

    # 填充数据
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE users SET email = username || '@example.com' WHERE email IS NULL")
    )

    # 设置非空约束
    op.alter_column('users', 'email', nullable=False)

def downgrade() -> None:
    # 删除列
    op.drop_column('users', 'email')
```

### 4. 团队协作

1. **Pull Request时包含迁移**
   - 永远不要在没有迁移的情况下修改模型
   - 确保迁移可以在空数据库上运行

2. **迁移审核**
   - 审查迁移SQL是否正确
   - 确保有适当的回滚逻辑

---

## 🐛 故障排除

### 常见错误

#### 1. 数据库连接错误

```bash
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**解决方案**:
```bash
# 确保数据库正在运行
docker-compose up postgres

# 检查连接字符串
echo $DATABASE_URL
```

#### 2. 迁移冲突

```bash
Target database is not up to date.
```

**解决方案**:
```bash
# 检查当前版本
alembic current

# 手动标记迁移
alembic stamp head
```

#### 3. 自动生成失败

```bash
alembic.util.exc.CommandError: Target database is not up to date.
```

**解决方案**:
```bash
# 升级到最新版本
alembic upgrade head

# 然后生成迁移
alembic revision --autogenerate -m "New migration"
```

---

## 📊 示例迁移

### 添加新表

```python
def upgrade() -> None:
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('theme', sa.String(50), nullable=True),
        sa.Column('language', sa.String(10), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_user_preferences_user_id', 'user_id'),
    )

def downgrade() -> None:
    op.drop_table('user_preferences')
```

### 添加新列

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'last_login')
```

### 重命名列

```python
def upgrade() -> None:
    op.alter_column('users', 'old_name', new_column_name='new_name')

def downgrade() -> None:
    op.alter_column('users', 'new_name', new_column_name='old_name')
```

### 添加索引

```python
def upgrade() -> None:
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

def downgrade() -> None:
    op.drop_index('ix_users_email', table_name='users')
```

---

## 🔐 安全注意事项

### 1. 生产环境

在生产环境中：

```bash
# 先备份数据库
pg_dump production_db > backup.sql

# 预览迁移SQL
alembic upgrade --sql head

# 在维护窗口执行
alembic upgrade head
```

### 2. 回滚计划

始终有回滚计划：

```python
def upgrade() -> None:
    # 危险操作前创建备份
    op.execute("CREATE TABLE users_backup AS SELECT * FROM users")

    # 执行变更
    op.alter_column('users', 'email', nullable=False)

def downgrade() -> None:
    # 恢复数据
    op.execute("DROP TABLE users")
    op.execute("ALTER TABLE users_backup RENAME TO users")
```

---

## 📚 参考资料

- [Alembic官方文档](https://alembic.sqlalchemy.org/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- [迁移最佳实践](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

---

## 💬 支持

如果您遇到迁移问题：

1. 检查日志: `docker-compose logs migration`
2. 查看文档: [Alembic文档](https://alembic.sqlalchemy.org/)
3. 创建Issue: 在项目中提交问题

---

**记住**: 数据库迁移是基础设施的重要部分，请谨慎操作！
