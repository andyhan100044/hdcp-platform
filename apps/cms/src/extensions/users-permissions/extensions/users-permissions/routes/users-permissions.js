'use strict';

module.exports = [
  {
    method: 'GET',
    path: '/users/me',
    handler: 'users-permissions.me',
    config: {
      policies: ['global::isAuthenticated'],
    },
  },
  {
    method: 'PUT',
    path: '/users/:id',
    handler: 'users-permissions.updateProfile',
    config: {
      policies: ['global::isAuthenticated'],
    },
  },
  {
    method: 'DELETE',
    path: '/users/:id',
    handler: 'users-permissions.delete',
    config: {
      policies: ['global::isAuthenticated'],
    },
  },
];
