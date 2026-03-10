import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // Chronos AI documentation sidebar
  docsSidebar: [
    {
      type: 'doc',
      id: 'user-guide',
      label: 'User Guide',
    },
    {
      type: 'doc',
      id: 'api-guide',
      label: 'API Guide',
    },
    {
      type: 'doc',
      id: 'agentic-thinking',
      label: 'Agentic Thinking',
    },
    {
      type: 'doc',
      id: 'playwright-deployment',
      label: 'Playwright Deployment',
    },
  ],
};

export default sidebars;
