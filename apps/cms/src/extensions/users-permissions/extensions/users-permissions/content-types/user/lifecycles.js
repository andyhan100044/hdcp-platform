'use strict';

const {anitize} = require('@strapi/utils');

module.exports = {
  async beforeCreate(event) {
    const { data } = event.params;

    // Auto-generate username from email if not provided
    if (data.email && !data.username) {
      data.username = data.email.split('@')[0];
    }

    // Set default locale
    if (!data.locale) {
      data.locale = 'en';
    }
  },

  async beforeUpdate(event) {
    // Handle user update logic if needed
  },

  async afterCreate(event) {
    const { result } = event;

    // Create profile if it doesn't exist
    if (!result.profile) {
      await strapi.entityService.create('component::user.profile', {
        data: {
          firstName: result.firstName || '',
          lastName: result.lastName || '',
          user: result.id
        }
      });
    }
  },

  async afterDelete(event) {
    // Clean up related data if needed
    const { result } = event;

    // Delete profile
    if (result.profile) {
      await strapi.entityService.delete('component::user.profile', result.profile.id);
    }
  }
};
