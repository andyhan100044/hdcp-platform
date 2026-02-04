'use strict';

const { createCoreController } = require('@strapi/strapi').factories;

module.exports = createCoreController('plugin::users-permissions.user', ({ strapi }) => ({
  /**
   * Get user profile
   */
  async me(ctx) {
    const user = ctx.state.user;

    if (!user) {
      return ctx.unauthorized();
    }

    const profile = await strapi.entityService.findOne('plugin::users-permissions.user', user.id, {
      populate: ['profile', 'role']
    });

    return profile;
  },

  /**
   * Update user profile
   */
  async updateProfile(ctx) {
    const { id } = ctx.params;
    const { body } = ctx.request;

    // Check if user is updating their own profile
    const user = ctx.state.user;
    if (!user || user.id !== parseInt(id)) {
      return ctx.unauthorized('You can only update your own profile');
    }

    // Update user
    const updatedUser = await strapi.entityService.update('plugin::users-permissions.user', id, {
      data: body,
      populate: ['profile', 'role']
    });

    return updatedUser;
  },

  /**
   * Get user by ID
   */
  async findOne(ctx) {
    const { id } = ctx.params;

    const user = await strapi.entityService.findOne('plugin::users-permissions.user', id, {
      populate: ['profile', 'role']
    });

    if (!user) {
      return ctx.notFound('User not found');
    }

    return user;
  },

  /**
   * Get all users with pagination
   */
  async find(ctx) {
    const { page = 1, pageSize = 10, sort = 'createdAt:desc' } = ctx.query;

    const users = await strapi.entityService.findMany('plugin::users-permissions.user', {
      populate: ['profile', 'role'],
      sort,
      pagination: {
        page: parseInt(page),
        pageSize: parseInt(pageSize)
      }
    });

    return users;
  },

  /**
   * Delete user
   */
  async delete(ctx) {
    const { id } = ctx.params;

    // Check if user exists
    const user = await strapi.entityService.findOne('plugin::users-permissions.user', id);
    if (!user) {
      return ctx.notFound('User not found');
    }

    // Delete user
    const deletedUser = await strapi.entityService.delete('plugin::users-permissions.user', id);

    return deletedUser;
  },

  /**
   * Update user role
   */
  async updateRole(ctx) {
    const { id } = ctx.params;
    const { role } = ctx.request.body;

    if (!role) {
      return ctx.badRequest('Role is required');
    }

    // Check if role exists
    const roleExists = await strapi.entityService.findOne('plugin::users-permissions.role', role);
    if (!roleExists) {
      return ctx.badRequest('Role does not exist');
    }

    const updatedUser = await strapi.entityService.update('plugin::users-permissions.user', id, {
      data: { role },
      populate: ['profile', 'role']
    });

    return updatedUser;
  },

  /**
   * Get user statistics
   */
  async statistics(ctx) {
    const [total, active, blocked] = await Promise.all([
      strapi.entityService.count('plugin::users-permissions.user'),
      strapi.entityService.count('plugin::users-permissions.user', { filters: { blocked: false } }),
      strapi.entityService.count('plugin::users-permissions.user', { filters: { blocked: true } })
    ]);

    return {
      total,
      active,
      blocked
    };
  }
}));
