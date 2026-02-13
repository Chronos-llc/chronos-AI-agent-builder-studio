export interface IconRegistryEntry {
  id: string
  name: string
  url: string
  aliases?: string[]
}

export type IconRegistryMap = Record<string, IconRegistryEntry>

export const aiProviders: IconRegistryMap = {
  openai: { id: 'openai', name: 'OpenAI', url: 'https://i.postimg.cc/d3HRsSv7/download_2.png' },
  anthropic: { id: 'anthropic', name: 'Anthropic', url: 'https://i.postimg.cc/Vkyrqc7m/download.jpg' },
  google: { id: 'google', name: 'Google', url: 'https://i.postimg.cc/2SwWrKwz/download_1.jpg' },
  fireworks: { id: 'fireworks', name: 'Fireworks', url: 'https://i.postimg.cc/rmvQqnL7/download_10.png' },
  xai: { id: 'xai', name: 'xAI', url: 'https://i.postimg.cc/zvbZ76dr/download.png' },
  openrouter: { id: 'openrouter', name: 'OpenRouter', url: 'https://i.postimg.cc/QdMMqLYZ/openrouter-icon.png' },
}

export const modelFamilies: IconRegistryMap = {
  gpt: { id: 'gpt', name: 'GPT', url: 'https://i.postimg.cc/d3HRsSv7/download_2.png' },
  gemini: { id: 'gemini', name: 'Gemini', url: 'https://i.postimg.cc/NMtZmLXT/download_4.png' },
  claude: { id: 'claude', name: 'Claude', url: 'https://i.postimg.cc/vBWbwprh/download_2.jpg' },
  llama: {
    id: 'llama',
    name: 'Llama',
    url: 'https://i.postimg.cc/ncd97sXP/download_12.png',
    aliases: ['llamma'],
  },
  grok: { id: 'grok', name: 'Grok', url: 'https://i.postimg.cc/Nj0VkW5g/download_1.png' },
}

export const sttTtsProviders: IconRegistryMap = {
  deepgram: { id: 'deepgram', name: 'Deepgram', url: 'https://i.postimg.cc/D01ZNZ62/download_4.jpg' },
  cartesia: { id: 'cartesia', name: 'Cartesia', url: 'https://i.postimg.cc/CxxhGJ35/download_15.png' },
  elevenlabs: { id: 'elevenlabs', name: 'ElevenLabs', url: 'https://i.postimg.cc/8CyrdjKZ/download_14.png' },
  openai: { id: 'openai', name: 'OpenAI', url: 'https://i.postimg.cc/d3HRsSv7/download_2.png' },
}

export const channels: IconRegistryMap = {
  slack: { id: 'slack', name: 'Slack', url: 'https://i.postimg.cc/vB84yFYN/download_24.png' },
  telegram: { id: 'telegram', name: 'Telegram', url: 'https://i.postimg.cc/KYsDGq2L/download_19.png' },
  whatsapp: { id: 'whatsapp', name: 'WhatsApp', url: 'https://i.postimg.cc/qRG2cxqh/download_23.png' },
  webchat: { id: 'webchat', name: 'Webchat', url: 'https://i.postimg.cc/3NKRXrZP/download-(1).png' },
  discord: { id: 'discord', name: 'Discord', url: 'https://i.postimg.cc/zfr1btpX/images-(1).png' },
}

export const integrationConnectors: IconRegistryMap = {
  web_browser: { id: 'web_browser', name: 'Web Browser', url: 'https://i.postimg.cc/8CyrdjKZ/download_14.png' },
  time: { id: 'time', name: 'Time', url: 'https://i.postimg.cc/1zxKSKjw/download_10.jpg' },
  notion: { id: 'notion', name: 'Notion', url: 'https://i.postimg.cc/bNzWcqt2/download_42.png' },
  github: { id: 'github', name: 'GitHub', url: 'https://i.postimg.cc/BZXzgmHC/download_27.png' },
  minimax: { id: 'minimax', name: 'MiniMax', url: 'https://i.postimg.cc/4dWHyh6N/download.png' },
  chrome: {
    id: 'chrome',
    name: 'Chrome Browser',
    url: 'https://i.postimg.cc/fyjzk4nP/internet_chrome_browser_logo_icon_symbol_vector_47573204.jpg',
  },
  serper: { id: 'serper', name: 'Serper', url: 'https://i.postimg.cc/jdYGSznk/download_7.jpg' },
  askui: { id: 'askui', name: 'Ask UI', url: 'https://i.postimg.cc/JzCN9ZPD/download.jpg' },
  sandbox_302ai: { id: 'sandbox_302ai', name: '302AI Sandbox', url: 'https://i.postimg.cc/3Nf1mQJf/download_37.png' },
  google_maps: { id: 'google_maps', name: 'Google Maps', url: 'https://i.postimg.cc/QCmPzzNQ/download_36.png' },
}

export const phoneProviders: IconRegistryMap = {
  twilio: {
    id: 'twilio',
    name: 'Twilio',
    url: 'https://i.postimg.cc/c45jzmKM/download_16.png',
    aliases: ['twillio'],
  },
  vonage: { id: 'vonage', name: 'Vonage', url: 'https://i.postimg.cc/fb5YHHyZ/download_18.png' },
}

export const landingGallery: string[] = [
  'https://i.postimg.cc/ZRBhMGJp/1764296890306(1).jpg',
  'https://i.postimg.cc/RhtdyR3J/Screenshot_20251128_031241_Photo_Editor.jpg',
  'https://i.postimg.cc/g2gFkzJL/1764296730418(1).jpg',
  'https://i.postimg.cc/htz6g9kS/1764296379324(1).jpg',
]

export const allProviderIcons = {
  ...aiProviders,
  ...sttTtsProviders,
  ...channels,
  ...integrationConnectors,
  ...phoneProviders,
}

export const getProviderIcon = (providerId: string): IconRegistryEntry | undefined => {
  const normalized = providerId.toLowerCase()
  const direct = allProviderIcons[normalized]
  if (direct) return direct

  const aliasHit = Object.values(allProviderIcons).find(entry =>
    entry.aliases?.some(alias => alias.toLowerCase() === normalized)
  )
  return aliasHit
}
