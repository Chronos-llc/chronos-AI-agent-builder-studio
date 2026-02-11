export interface TelegramConfig {
  [key: string]: any
}

export interface SlackConfig {
  [key: string]: any
}

export interface WhatsAppConfig {
  [key: string]: any
}

export interface DiscordConfig {
  [key: string]: any
}

export interface WebChatConfig {
  [key: string]: any
}

export interface ChannelConfig {
  telegram?: TelegramConfig
  slack?: SlackConfig
  whatsapp?: WhatsAppConfig
  discord?: DiscordConfig
  webchat?: WebChatConfig
  [key: string]: any
}

