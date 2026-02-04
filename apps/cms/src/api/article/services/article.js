'use strict';

const { createCoreService } = require('@strapi/strapi').factories;

module.exports = createCoreService('api::article.article', ({ strapi }) => ({
  /**
   * Get articles with pagination and filters
   */
  async getArticles(params = {}) {
    const {
      page = 1,
      pageSize = 10,
      sort = 'publishedAt:desc',
      populate = ['category', 'tags', 'author', 'cover_image'],
      filters = {}
    } = params;

    return await strapi.entityService.findMany('api::article.article', {
      filters,
      populate,
      sort,
      pagination: {
        page: parseInt(page),
        pageSize: parseInt(pageSize)
      }
    });
  },

  /**
   * Get article by ID or slug
   */
  async getArticle(identifier) {
    let article;

    if (identifier.match(/^\d+$/)) {
      article = await strapi.entityService.findOne('api::article.article', identifier, {
        populate: ['category', 'tags', 'author', 'cover_image', 'seo']
      });
    } else {
      const articles = await strapi.entityService.findMany('api::article.article', {
        filters: { slug: identifier },
        populate: ['category', 'tags', 'author', 'cover_image', 'seo'],
        limit: 1
      });
      article = articles[0];
    }

    return article;
  },

  /**
   * Get featured articles
   */
  async getFeaturedArticles(limit = 5) {
    return await strapi.entityService.findMany('api::article.article', {
      filters: {
        featured: true,
        status: 'published'
      },
      populate: ['category', 'tags', 'author', 'cover_image'],
      sort: { publishedAt: 'desc' },
      limit: parseInt(limit)
    });
  },

  /**
   * Get articles by category
   */
  async getArticlesByCategory(categoryId, params = {}) {
    const {
      page = 1,
      pageSize = 10,
      sort = 'publishedAt:desc'
    } = params;

    return await strapi.entityService.findMany('api::article.article', {
      filters: {
        category: categoryId,
        status: 'published'
      },
      populate: ['category', 'tags', 'author', 'cover_image'],
      sort,
      pagination: {
        page: parseInt(page),
        pageSize: parseInt(pageSize)
      }
    });
  },

  /**
   * Search articles
   */
  async searchArticles(query, params = {}) {
    const {
      page = 1,
      pageSize = 10,
      sort = 'publishedAt:desc'
    } = params;

    return await strapi.entityService.findMany('api::article.article', {
      filters: {
        $or: [
          { title: { $containsi: query } },
          { excerpt: { $containsi: query } },
          { content: { $containsi: query } }
        ],
        status: 'published'
      },
      populate: ['category', 'tags', 'author', 'cover_image'],
      sort,
      pagination: {
        page: parseInt(page),
        pageSize: parseInt(pageSize)
      }
    });
  },

  /**
   * Get related articles
   */
  async getRelatedArticles(articleId, limit = 5) {
    const article = await strapi.entityService.findOne('api::article.article', articleId);

    if (!article) {
      return null;
    }

    return await strapi.entityService.findMany('api::article.article', {
      filters: {
        id: { $ne: articleId },
        category: article.category?.id,
        status: 'published'
      },
      populate: ['category', 'tags', 'author', 'cover_image'],
      sort: { publishedAt: 'desc' },
      limit: parseInt(limit)
    });
  },

  /**
   * Get articles statistics
   */
  async getStatistics() {
    const [total, published, draft, featured] = await Promise.all([
      strapi.entityService.count('api::article.article'),
      strapi.entityService.count('api::article.article', { filters: { status: 'published' } }),
      strapi.entityService.count('api::article.article', { filters: { status: 'draft' } }),
      strapi.entityService.count('api::article.article', { filters: { featured: true } })
    ]);

    return {
      total,
      published,
      draft,
      featured
    };
  },

  /**
   * Increment view count
   */
  async incrementViewCount(articleId) {
    const article = await strapi.entityService.findOne('api::article.article', articleId);

    if (article) {
      await strapi.entityService.update('api::article.article', articleId, {
        data: { viewCount: (article.viewCount || 0) + 1 }
      });
    }
  },

  /**
   * Calculate reading time
   */
  calculateReadingTime(content) {
    const wordsPerMinute = 200;
    const textContent = content.replace(/<[^>]*>/g, ''); // Remove HTML tags
    const wordCount = textContent.split(/\s+/).length;
    const readingTime = Math.ceil(wordCount / wordsPerMinute);

    return readingTime;
  },

  /**
   * Auto-generate slug
   */
  async generateSlug(title) {
    const slug = title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');

    // Check if slug exists
    const existingArticles = await strapi.entityService.findMany('api::article.article', {
      filters: { slug: { $containsi: slug } },
      fields: ['slug']
    });

    if (existingArticles.length === 0) {
      return slug;
    }

    // Add number if slug exists
    let counter = 1;
    let newSlug = `${slug}-${counter}`;

    while (existingArticles.some(article => article.slug === newSlug)) {
      counter++;
      newSlug = `${slug}-${counter}`;
    }

    return newSlug;
  }
}));
