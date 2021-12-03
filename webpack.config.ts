import path from 'path';
import { Configuration } from 'webpack';
import TsconfigPathsPlugin from 'tsconfig-paths-webpack-plugin';
import nodeExternals from 'webpack-node-externals';

const config: Configuration = {
  mode: process.env.NODE_ENV as 'development' | 'production',
  target: 'node',
  context: path.join(__dirname, 'src'),
  entry: './index.ts',
  output: {
    filename: 'index.js',
    path: path.resolve(__dirname, 'build'),
  },
  resolve: {
    plugins: [new TsconfigPathsPlugin()],
    extensions: ['.ts'],
  },
  module: {
    rules: [{ test: /\.ts?$/, loader: 'ts-loader' }],
  },
  externals: [nodeExternals()],
};

export default config;