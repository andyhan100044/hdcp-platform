'use strict';

const { yup, validateYupSchema } = require('@strapi/utils');

const callbackSchema = yup.object({
  params: yup.object({
    identifier: yup.string().required(),
    password: yup.string().required(),
  }),
});

const registerSchema = yup.object({
  body: yup.object({
    email: yup.string().email().required(),
    username: yup.string().min(3).required(),
    password: yup.string().min(6).required(),
    firstName: yup.string(),
    lastName: yup.string(),
    locale: yup.string().oneOf(['en', 'zh-CN', 'es', 'fr', 'de', 'ja', 'ko', 'ar']),
  }),
});

const forgotPasswordSchema = yup.object({
  body: yup.object({
    email: yup.string().email().required(),
  }),
});

const resetPasswordSchema = yup.object({
  body: yup.object({
    code: yup.string().required(),
    password: yup.string().min(6).required(),
    passwordConfirmation: yup.string().oneOf([yup.ref('password'), null]).required(),
  }),
});

module.exports = {
  validateCallback: validateYupSchema(callbackSchema),
  validateRegisterBody: validateYupSchema(registerSchema),
  validateForgotPasswordBody: validateYupSchema(forgotPasswordSchema),
  validateResetPasswordBody: validateYupSchema(resetPasswordSchema),
};
