// remotion.config.js
const { defineWebpackConfig } = require('@remotion/bundler');

module.exports = {
  webpack: defineWebpackConfig({
    resolve: {
      fallback: {
        path: require.resolve('path-browserify'),
        fs: false,  // We don't need fs in the browser
        child_process: false,  // We don't need child_process in the browser
      },
    },
  }),
};


