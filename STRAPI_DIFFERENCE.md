# Strapi 与 HDCP CMS 的区别

## 🤔 你的问题：到底有什么区别？

### 🎯 **直接回答**

**Strapi = 通用CMS框架**
**HDCP CMS = 基于Strapi的**业务定制CMS****

---

## 📊 **对比表**

| 方面 | Strapi 官方 | HDCP CMS (我们的) |
|------|-------------|----------------|
| **性质** | 通用CMS | 业务定制CMS |
| **用户** | 任何开发者 | HDCP平台专用 |
| **数据模型** | 通用字段 | 业务特定字段 |
| **API** | 通用API | 业务API |
| **界面** | 通用管理后台 | 业务定制界面 |
| **功能** | 基础CRUD | 业务逻辑+CRUD |

---

## 🔍 **具体区别**

### Strapi 官方的数据模型

```json
{
  "name": "Article",
  "attributes": {
    "title": { "type": "string" },
    "content": { "type": "text" },
    "published": { "type": "boolean" }
  }
}
```

**特点：**
- ✅ 通用字段
- ✅ 任何人都能用
- ❌ 没有业务逻辑

---

### HDCP CMS 的数据模型

```json
{
  "name": "Article",
  "attributes": {
    "title": { "type": "string" },
    "slug": { "type": "uid" },
    "content": { "type": "richtext" },
    "excerpt": { "type": "text" },
    "cover_image": { "type": "media" },
    "category": { "type": "relation" },
    "tags": { "type": "relation" },
    "author": { "type": "relation" },
    "publishedAt": { "type": "datetime" },
    "readingTime": { "type": "integer" },
    "viewCount": { "type": "integer" },
    "featured": { "type": "boolean" },
    "seo": { "type": "component" }
  }
}
```

**特点：**
- ✅ 业务特定字段 (readingTime, viewCount, featured)
- ✅ SEO组件
- ✅ 关系型字段
- ✅ 媒体支持

---

## 🏗️ **代码区别**

### Strapi 官方 Controller (简单)

```javascript
// Strapi 自动生成的通用 Controller
'use strict';

const { createCoreController } = require('@strapi/strapi').factories;

module.exports = createCoreController('api::article.article');
```

**特点：**
- ❌ 只有基本 CRUD
- ❌ 没有业务逻辑
- ❌ 没有过滤、搜索

---

### HDCP CMS Controller (复杂)

```javascript
'use strict';

const { createCoreController } = require('@strapi/strapi').factories;

module.exports = createCoreController('api::article.article', ({ strapi }) => ({
  // ✅ 自定义业务逻辑
  async find(ctx) {
    const { query } = ctx;
    const defaultFilters = {
      ...query,
      'filters[status][$eq]': 'published'
    };

    const articles = await strapi.entityService.findMany('api::article.article', {
      ...defaultFilters,
      populate: ['category', 'tags', 'author', 'cover_image', 'seo']
    });

    return articles;
  },

  // ✅ 精选文章
  async featured(ctx) {
    const { limit = 5 } = ctx.query;
    const articles = await strapi.entityService.findMany('api::article.article', {
      filters: {
        featured: true,
        status: 'published'
      },
      populate: ['category', 'tags', 'author', 'cover_image'],
      sort: { publishedAt: 'desc' },
      limit: parseInt(limit)
    });
    return articles;
  },

  // ✅ 按分类获取
  async byCategory(ctx) {
    const { categoryId } = ctx.params;
    const { page = 1, pageSize = 10 } = ctx.query;

    const articles = await strapi.entityService.findMany('api::article.article', {
      filters: {
        category: categoryId,
        status: 'published'
      },
      populate: ['category', 'tags', 'author', 'cover_image'],
      sort: { publishedAt: 'desc' },
      pagination: { page, pageSize }
    });
    return articles;
  },

  // ✅ 搜索功能
  async search(ctx) {
    const { q: query, page = 1, pageSize = 10 } = ctx.query;
    const articles = await strapi.entityService.findMany('api::article.article', {
      filters: {
        $or: [
          { title: { $containsi: query } },
          { excerpt: { $containsi: query } },
          { content: { $containsi: query } }
        ],
        status: 'published'
      },
      populate: ['category', 'tags', 'author', 'cover_image'],
      sort: { publishedAt: 'desc' },
      pagination: { page, pageSize }
    });
    return articles;
  },

  // ✅ 相关文章
  async related(ctx) {
    const { id } = ctx.params;
    const { limit = 5 } = ctx.query;

    const article = await strapi.entityService.findOne('api::article.article', id);
    const relatedArticles = await strapi.entityService.findMany('api::article.article', {
      filters: {
        id: { $ne: id },
        category: article.category?.id,
        status: 'published'
      },
      populate: ['category', 'tags', 'author', 'cover_image'],
      sort: { publishedAt: 'desc' },
      limit: parseInt(limit)
    });
    return relatedArticles;
  },

  // ✅ 访问统计
  async findOne(ctx) {
    const { id } = ctx.params;
    let article;

    if (id.match(/^\d+$/)) {
      article = await strapi.entityService.findOne('api::article.article', id, {
        populate: ['category', 'tags', 'author', 'cover_image', 'seo']
      });
    } else {
      const articles = await strapi.entityService.findMany('api::article.article', {
        filters: { slug: id },
        populate: ['category', 'tags', 'author', 'cover_image', 'seo'],
        limit: 1
      });
      article = articles[0];
    }

    // ✅ 业务逻辑：访问量统计
    if (ctx.method === 'GET' && article) {
      await strapi.entityService.update('api::article.article', article.id, {
        data: { viewCount: (article.viewCount || 0) + 1 }
      });
    }

    return article;
  }
}));
```

**特点：**
- ✅ 206行代码
- ✅ 8个自定义方法
- ✅ 复杂业务逻辑
- ✅ 访问统计
- ✅ 搜索、筛选、推荐

---

## 🔧 **Service 区别**

### Strapi 官方 Service (无)

```javascript
// Strapi 不提供自定义 Service
// 只有默认的 entityService
```

---

### HDCP CMS Service (有)

```javascript
'use strict';

const { createCoreService } = require('@strapi/strapi').factories;

module.exports = createCoreService('api::article.article', ({ strapi }) => ({
  // ✅ 计算阅读时间
  calculateReadingTime(content) {
    const wordsPerMinute = 200;
    const textContent = content.replace(/<[^>]*>/g, '');
    const wordCount = textContent.split(/\s+/).length;
    const readingTime = Math.ceil(wordCount / wordsPerMinute);
    return readingTime;
  },

  // ✅ 自动生成 Slug
  async generateSlug(title) {
    const slug = title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');

    const existingArticles = await strapi.entityService.findMany('api::article.article', {
      filters: { slug: { $containsi: slug } },
      fields: ['slug']
    });

    if (existingArticles.length === 0) {
      return slug;
    }

    let counter = 1;
    let newSlug = `${slug}-${counter}`;

    while (existingArticles.some(article => article.slug === newSlug)) {
      counter++;
      newSlug = `${slug}-${counter}`;
    }

    return newSlug;
  },

  // ✅ 获取统计
  async getStatistics() {
    const [total, published, draft, featured] = await Promise.all([
      strapi.entityService.count('api::article.article'),
      strapi.entityService.count('api::article.article', { filters: { status: 'published' } }),
      strapi.entityService.count('api::article.article', { filters: { status: 'draft' } }),
      strapi.entityService.count('api::article.article', { filters: { featured: true } })
    ]);

    return { total, published, draft, featured };
  },

  // ✅ 增量访问量
  async incrementViewCount(articleId) {
    const article = await strapi.entityService.findOne('api::article.article', articleId);
    if (article) {
      await strapi.entityService.update('api::article.article', articleId, {
        data: { viewCount: (article.viewCount || 0) + 1 }
      });
    }
  }
}));
```

**特点：**
- ✅ 214行代码
- ✅ 4个自定义方法
- ✅ 业务逻辑
- ✅ 统计功能

---

## 📦 **插件 vs 定制**

### Strapi 插件模式

```bash
# 安装插件
npm install @strapi/plugin-graphql
npm install @strapi/plugin-i18n
npm install @strapi/plugin-users-permissions

# 配置插件
# config/plugins.js
module.exports = {
  graphql: {
    enabled: true,
    config: { ... }
  }
};
```

**特点：**
- ✅ 通用插件
- ✅ 任何项目都能用
- ❌ 没有业务逻辑

---

### HDCP 定制代码

```bash
# 我们的定制代码
# apps/cms/src/api/article/
# ├── content-types/article/schema.json  ← 自定义数据模型
# ├── controllers/article.js            ← 自定义控制器
# ├── services/article.js              ← 自定义服务
# └── routes/article.js                ← 自定义路由

# apps/cms/src/components/
# ├── shared/seo.json                  ← 自定义组件
# └── user/profile.json               ← 用户配置

# apps/cms/src/middlewares/
# ├── is-authenticated.js              ← 自定义中间件
# └── rate-limit.js                   ← 业务限制
```

**特点：**
- ✅ 业务定制
- ✅ 专用功能
- ✅ 复杂逻辑

---

## 🎯 **总结**

### Strapi 官方 CMS

| 特点 | 优势 | 劣势 |
|------|------|------|
| 通用性 | ✅ 任何项目都能用 | ❌ 没有业务逻辑 |
| 易用性 | ✅ 快速搭建 | ❌ 需要大量定制 |
| 功能 | ✅ 基础功能完善 | ❌ 缺少业务功能 |
| 复杂度 | ✅ 低 | ❌ 需要额外开发 |

---

### HDCP CMS (我们的)

| 特点 | 优势 | 劣势 |
|------|------|------|
| 业务性 | ✅ 专为HDCP定制 | ❌ 通用性差 |
| 功能性 | ✅ 业务逻辑完整 | ❌ 复杂度高 |
| 性能 | ✅ 优化特定场景 | ❌ 不适合其他场景 |
| 维护 | ✅ 业务逻辑清晰 | ❌ 需要专业知识 |

---

## 🚀 **结论**

### 我们和Strapi的关系

```
HDCP CMS = Strapi 框架 + 我们的定制代码

Strapi 框架:
├── ✅ 数据库连接
├── ✅ Admin UI
├── ✅ 权限系统
├── ✅ 文件上传
├── ✅ 插件系统
└── ✅ GraphQL 生成

我们的定制代码:
├── ✅ 业务数据模型
├── ✅ 业务控制器
├── ✅ 业务服务
├── ✅ 业务中间件
└── ✅ 业务组件
```

### 🎯 **一句话总结**

**Strapi 是插件模式的通用框架，**
**我们的 HDCP CMS 是基于Strapi的业务定制实现，**
**专门为HDCP平台优化，包含复杂的业务逻辑和功能。**

**就像 WordPress 是通用CMS，**
**但每个定制主题都是独特的。** 🚀
