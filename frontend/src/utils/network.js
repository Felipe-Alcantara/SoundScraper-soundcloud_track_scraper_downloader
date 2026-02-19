const isBrowser = typeof window !== 'undefined'

const pageProtocol = isBrowser ? window.location.protocol : 'http:'
const pageHost = isBrowser ? window.location.host : '127.0.0.1:8000'
const pageOrigin = isBrowser ? window.location.origin : 'http://127.0.0.1:8000'

const inferredWsFromApi = (apiOrigin) => (
  apiOrigin.startsWith('https://')
    ? apiOrigin.replace('https://', 'wss://')
    : apiOrigin.replace('http://', 'ws://')
)

const devApiOrigin = (import.meta.env.VITE_API_ORIGIN || 'http://127.0.0.1:8000').replace(/\/+$/, '')
const devWsOrigin = (import.meta.env.VITE_WS_ORIGIN || inferredWsFromApi(devApiOrigin)).replace(/\/+$/, '')

const runtimeWsOrigin = `${pageProtocol === 'https:' ? 'wss:' : 'ws:'}//${pageHost}`

export const API_ORIGIN = import.meta.env.DEV ? devApiOrigin : pageOrigin
export const WS_ORIGIN = import.meta.env.DEV ? devWsOrigin : runtimeWsOrigin

export function buildApiUrl(path) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${API_ORIGIN}${normalizedPath}`
}

export function buildWsUrl(path) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${WS_ORIGIN}${normalizedPath}`
}

