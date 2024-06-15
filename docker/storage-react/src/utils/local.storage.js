// utils/local.storage.js

const ENV_KEY = 'selectedEnvironment';

export const getEnvironment = () => {
 return localStorage.getItem(ENV_KEY) || 'prod';
};

export const setEnvironment = (env) => {
 localStorage.setItem(ENV_KEY, env);
};
