'use strict';

module.exports = {
  routes: [
    {
      method: 'GET',
      path: '/navigation-items',
      handler: 'navigation-item.find',
      config: {
        policies: [],
        middlewares: [],
      },
    },
    {
      method: 'POST',
      path: '/navigation-items',
      handler: 'navigation-item.create',
      config: {
        policies: [],
        middlewares: [],
      },
    },
    {
      method: 'PUT',
      path: '/navigation-items/:id',
      handler: 'navigation-item.update',
      config: {
        policies: [],
        middlewares: [],
      },
    },
    {
      method: 'DELETE',
      path: '/navigation-items/:id',
      handler: 'navigation-item.delete',
      config: {
        policies: [],
        middlewares: [],
      },
    },
    {
      method: 'POST',
      path: '/navigation-items/reorder',
      handler: 'navigation-item.reorder',
      config: {
        policies: [],
        middlewares: [],
      },
    },
  ],
};
