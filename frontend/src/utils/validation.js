const USERNAME_PATTERN = /^[a-z0-9_-]+$/i

function isSoundCloudHost(hostname) {
  return hostname === 'soundcloud.com' || hostname === 'www.soundcloud.com'
}

export function isValidSoundCloudInput(value) {
  const trimmed = value.trim()
  if (!trimmed) return false

  const candidate = trimmed.includes('://') ? trimmed : `https://${trimmed}`
  try {
    const url = new URL(candidate)
    if (isSoundCloudHost(url.hostname)) {
      return url.pathname.split('/').filter(Boolean).length > 0
    }
  } catch {
    return false
  }

  return USERNAME_PATTERN.test(trimmed)
}
