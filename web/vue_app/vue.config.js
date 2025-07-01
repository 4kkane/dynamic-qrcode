const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  outputDir: '../dist',
  publicPath: './',
  devServer: {
    proxy: {
      '/dcode': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/qrcodes': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})