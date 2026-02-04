'use strict';

module.exports = async (ctx, next) => {
  const { id } = ctx.params;
  const user = ctx.state.user;

  if (!user) {
    return ctx.unauthorized('You must be authenticated');
  }

  // Check if user is owner of the resource
  if (user.id !== parseInt(id)) {
    return ctx.unauthorized('You can only access your own resources');
  }

  await next();
};
