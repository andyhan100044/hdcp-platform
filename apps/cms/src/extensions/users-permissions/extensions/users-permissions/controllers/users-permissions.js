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
   * Delete user
   */
  async delete(ctx) {
    const { id } = ctx.params;

    const deletedUser = await strapi.entityService.delete('plugin::users-permissions.user', id);

    return deletedUser;
  }
}));
