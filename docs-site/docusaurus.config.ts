import {type Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import type * as RD from '@docusaurus/theme-redoc';

const config: Config = {
  title: 'Chronos Studio',
  tagline: 'AI Agent Builder Platform',
  url: 'https://chronosllc0.github.io',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',

  organizationName: 'Chronos-llc',
  projectName: 'chronos-AI-agent-builder-studio',

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/Chronos-llc/chronos-AI-agent-builder-studio/tree/main/docs-site/docs/',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],
};

export default config;
