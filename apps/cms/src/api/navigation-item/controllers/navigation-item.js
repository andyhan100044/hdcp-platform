'use strict';

const { createCoreController } = require('@strapi/strapi').factories;

module.exports = createCoreController('api::navigation-item.navigation-item', ({ strapi }) => ({
  /**
   * Get all navigation items sorted by order
   */
  async find(ctx) {
    const navigationItems = await strapi.entityService.findMany('api::navigation-item.navigation-item', {
      populate: ['parent', 'children'],
      sort: { order: 'asc' }
    });

    // Build hierarchical structure
    const hierarchical = buildHierarchy(navigationItems);

    return hierarchical;
  },

  /**
   * Create navigation item
   */
  async create(ctx) {
    const { data } = ctx.request.body;

    const navigationItem = await strapi.entityService.create('api::navigation-item.navigation-item', {
      data,
      populate: ['parent', 'children']
    });

    return navigationItem;
  },

  /**
   * Update navigation item
   */
  async update(ctx) {
    const { id } = ctx.params;
    const { data } = ctx.request.body;

    const navigationItem = await strapi.entityService.update('api::navigation-item.navigation-item', id, {
      data,
      populate: ['parent', 'children']
    });

    return navigationItem;
  },

  /**
   * Delete navigation item
   */
  async delete(ctx) {
    const { id } = ctx.params;

    const navigationItem = await strapi.entityService.delete('api::navigation-item.navigation-item', id);

    return navigationItem;
  },

  /**
   * Reorder navigation items
   */
  async reorder(ctx) {
    const { items } = ctx.request.body;

    if (!Array.isArray(items)) {
      return ctx.badRequest('Items must be an array');
    }

    // Update order for each item
    const updatePromises = items.map((item, index) =>
      strapi.entityService.update('api::navigation-item.navigation-item', item.id, {
        data: { order: index }
      })
    );

    await Promise.all(updatePromises);

    // Return updated navigation
    const navigationItems = await strapi.entityService.findMany('api::navigation-item.navigation-item', {
      populate: ['parent', 'children'],
      sort: { order: 'asc' }
    });

    return buildHierarchy(navigationItems);
  }
}));

function buildHierarchy(items, parentId = null) {
  return items
    .filter(item => item.parent?.id === parentId)
    .map(item => ({
      ...item,
      children: buildHierarchy(items, item.id)
    }));
}
