'use strict';

const { createCoreService } = require('@strapi/strapi').factories;

module.exports = createCoreService('api::page.page', ({ strapi }) => ({
  /**
   * Get page by ID or slug
   */
  async getPage(identifier) {
    let page;

    if (identifier.match(/^\d+$/)) {
      page = await strapi.entityService.findOne('api::page.page', identifier, {
        populate: ['seo']
      });
    } else {
      const pages = await strapi.entityService.findMany('api::page.page', {
        filters: { slug: identifier },
        populate: ['seo'],
        limit: 1
      });
      page = pages[0];
    }

    return page;
  },

  /**
   * Get all pages
   */
  async getPages(params = {}) {
    const { sort = 'createdAt:desc' } = params;

    return await strapi.entityService.findMany('api::page.page', {
      populate: ['seo'],
      sort
    });
  },

  /**
   * Generate slug from title
   */
  async generateSlug(title) {
    const slug = title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');

    // Check if slug exists
    const existingPages = await strapi.entityService.findMany('api::page.page', {
      filters: { slug: { $containsi: slug } },
      fields: ['slug']
    });

    if (existingPages.length === 0) {
      return slug;
    }

    // Add number if slug exists
    let counter = 1;
    let newSlug = `${slug}-${counter}`;

    while (existingPages.some(page => page.slug === newSlug)) {
      counter++;
      newSlug = `${slug}-${counter}`;
    }

    return newSlug;
  }
}));
