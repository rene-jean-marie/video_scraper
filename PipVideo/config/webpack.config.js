'use strict';

const { merge } = require('webpack-merge');
const path = require('path');

const common = require('./webpack.common.js');
const PATHS = require('./paths');

// Merge webpack configuration files
const config = merge(common, {
  entry: {
    devtools: PATHS.src + '/devtools.js',
    panel: PATHS.src + '/panel.js',
    background: path.resolve(__dirname, '../pipvideo.js'),
    popup: PATHS.src + '/popup.js',
    content: PATHS.src + '/content.js',
  },
});

module.exports = config;
