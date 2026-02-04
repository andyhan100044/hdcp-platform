'use strict';

const { createCoreController } = require('@strapi/strapi').factories;

module.exports = createCoreController('api::page.page', ({ strapi }) => ({
  /**
   * Get page by slug
   */
  async findOne(ctx) {
    const { id } = ctx.params;

    let page;

    // Try to find by ID first
    if (id.match(/^\d+$/)) {
      page = await strapi.entityService.findOne('api::page.page', id, {
        populate: ['seo']
      });
    } else {
      // Find by slug
      const pages = await strapi.entityService.findMany('api::page.page', {
        filters: { slug: id },
        populate: ['seo'],
        limit: 1
      });
      page = pages[0];
    }

    if (!page) {
      return ctx.notFound('Page not found');
    }

    return page;
  },

  /**
   * Get all pages
   */
  async find(ctx) {
    const pages = await strapi.entityService.findMany('api::page.page', {
      populate: ['seo'],
      sort: { createdAt: 'desc' }
    });

    return pages;
  },

  /**
   * Create page
   */
  async create(ctx) {
    const { data } = ctx.request.body;

    data.status = data.status || 'draft';
    data.locale = data.locale || 'en';

    const page = await strapi.entityService.create('api::page.page', {
      data,
      populate: ['seo']
    });

    return page;
  },

  /**
   * Update page
   */
  async update(ctx) {
    const { id } = ctx.params;
    const { data } = ctx.request.body;

    const page = await strapi.entityService.update('api::page.page', id, {
      data,
      populate: ['seo']
    });

    return page;
  },

  /**
   * Delete page
   */
  async delete(ctx) {
    const { id } = ctx.params;

    const page = await strapi.entityService.delete('api::page.page', id);

    return page;
  }
}));
