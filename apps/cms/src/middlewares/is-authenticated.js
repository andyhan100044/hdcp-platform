'use strict';

module.exports = async (ctx, next) => {
  if (!ctx.state.user) {
    return ctx.unauthorized('You must be authenticated to access this resource');
  }

  await next();
};
