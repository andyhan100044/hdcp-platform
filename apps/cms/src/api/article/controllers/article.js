'use strict';

const { createCoreController } = require('@strapi/strapi').factories;

module.exports = createCoreController('api::article.article', ({ strapi }) => ({
  /**
   * Get published articles
   */
  async find(ctx) {
    const { query } = ctx;

    // Add default filters for published articles
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

  /**
   * Get article by slug
   */
  async findOne(ctx) {
    const { id } = ctx.params;

    let article;

    // Try to find by ID first
    if (id.match(/^\d+$/)) {
      article = await strapi.entityService.findOne('api::article.article', id, {
        populate: ['category', 'tags', 'author', 'cover_image', 'seo']
      });
    } else {
      // Find by slug
      const articles = await strapi.entityService.findMany('api::article.article', {
        filters: { slug: id },
        populate: ['category', 'tags', 'author', 'cover_image', 'seo'],
        limit: 1
      });
      article = articles[0];
    }

    if (!article) {
      return ctx.notFound('Article not found');
    }

    // Increment view count
    if (ctx.method === 'GET') {
      await strapi.entityService.update('api::article.article', article.id, {
        data: { viewCount: (article.viewCount || 0) + 1 }
      });
    }

    return article;
  },

  /**
   * Get featured articles
   */
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

  /**
   * Get articles by category
   */
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
      pagination: {
        page: parseInt(page),
        pageSize: parseInt(pageSize)
      }
    });

    return articles;
  },

  /**
   * Search articles
   */
  async search(ctx) {
    const { q: query, page = 1, pageSize = 10 } = ctx.query;

    if (!query) {
      return ctx.badRequest('Search query is required');
    }

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
      pagination: {
        page: parseInt(page),
        pageSize: parseInt(pageSize)
      }
    });

    return articles;
  },

  /**
   * Get related articles
   */
  async related(ctx) {
    const { id } = ctx.params;
    const { limit = 5 } = ctx.query;

    const article = await strapi.entityService.findOne('api::article.article', id);

    if (!article) {
      return ctx.notFound('Article not found');
    }

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

  /**
   * Create article
   */
  async create(ctx) {
    const { data } = ctx.request.body;

    // Set default values
    data.status = data.status || 'draft';
    data.viewCount = 0;
    data.locale = data.locale || 'en';

    const article = await strapi.entityService.create('api::article.article', {
      data,
      populate: ['category', 'tags', 'author', 'cover_image', 'seo']
    });

    return article;
  },

  /**
   * Update article
   */
  async update(ctx) {
    const { id } = ctx.params;
    const { data } = ctx.request.body;

    const article = await strapi.entityService.update('api::article.article', id, {
      data,
      populate: ['category', 'tags', 'author', 'cover_image', 'seo']
    });

    return article;
  },

  /**
   * Delete article
   */
  async delete(ctx) {
    const { id } = ctx.params;

    const article = await strapi.entityService.delete('api::article.article', id);

    return article;
  }
}));
