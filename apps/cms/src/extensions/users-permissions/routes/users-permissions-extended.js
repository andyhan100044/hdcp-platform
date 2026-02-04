'use strict';

module.exports = {
  routes: [
    {
      method: 'GET',
      path: '/users/me',
      handler: 'users-permissions-extended.me',
      config: {
        policies: ['global::isAuthenticated'],
        middlewares: [],
      },
    },
    {
      method: 'PUT',
      path: '/users/:id',
      handler: 'users-permissions-extended.updateProfile',
      config: {
        policies: ['global::isAuthenticated'],
        middlewares: [],
      },
    },
    {
      method: 'GET',
      path: '/users/statistics',
      handler: 'users-permissions-extended.statistics',
      config: {
        policies: ['global::isAuthenticated'],
        middlewares: [],
      },
    },
    {
      method: 'GET',
      path: '/users/:id',
      handler: 'users-permissions-extended.findOne',
      config: {
        policies: ['global::isAuthenticated'],
        middlewares: [],
      },
    },
    {
      method: 'PUT',
      path: '/users/:id/role',
      handler: 'users-permissions-extended.updateRole',
      config: {
        policies: ['global::isAuthenticated'],
        middlewares: [],
      },
    },
    {
      method: 'DELETE',
      path: '/users/:id',
      handler: 'users-permissions-extended.delete',
      config: {
        policies: ['global::isAuthenticated'],
        middlewares: [],
      },
    },
  ],
};
