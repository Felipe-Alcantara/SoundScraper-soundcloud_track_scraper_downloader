import { useState } from 'react'
import Button from './ui/Button'
import Input from './ui/Input'
import Badge from './ui/Badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card'
import { cx } from '../utils/cx'
import { isValidSoundCloudInput } from '../utils/validation'

const OPTIONS = [
  { value: '1', label: 'Todas', icon: '📀' },
  { value: '2', label: 'Populares', icon: '🔥' },
  { value: '3', label: 'Faixas', icon: '🎵' },
  { value: '4', label: 'Álbuns', icon: '💿' },
  { value: '5', label: 'Playlists', icon: '📋' },
  { value: '6', label: 'Reposts', icon: '🔁' },
  { value: '7', label: 'Curtidas', icon: '❤️' },
]

function UrlInput({ onScrapeStart }) {
  const [url, setUrl] = useState('')
  const [choice, setChoice] = useState('3')

  const trimmedUrl = url.trim()
  const isValidUrl = isValidSoundCloudInput(trimmedUrl)

  const handleSubmit = (event) => {
    event.preventDefault()
    if (!isValidUrl) return
    onScrapeStart(trimmedUrl, choice)
  }

  return (
    <Card className="felixo-card-glow">
      <CardHeader>
        <div className="flex flex-wrap items-center gap-3">
          <CardTitle className="text-lg">Coletar Links do SoundCloud</CardTitle>
          <Badge className="bg-felixo-purple/10 text-felixo-purple border-felixo-purple/35">
            Etapa 1
          </Badge>
        </div>
        <CardDescription className="mt-2">
          Cole um perfil/URL e escolha o tipo de coleção para iniciar a coleta em tempo real.
        </CardDescription>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="soundcloud-url" className="block text-sm text-zinc-300">
              Link do SoundCloud
            </label>
            <Input
              id="soundcloud-url"
              type="text"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              placeholder="soundcloud.com/artista ou https://soundcloud.com/artista"
              aria-invalid={Boolean(trimmedUrl) && !isValidUrl}
              aria-describedby={trimmedUrl && !isValidUrl ? 'soundcloud-url-error' : undefined}
            />
            {trimmedUrl && !isValidUrl && (
              <p id="soundcloud-url-error" className="text-xs text-red-300" role="alert">
                Formato inválido. Use um link SoundCloud ou nome de perfil.
              </p>
            )}
          </div>

          <fieldset className="space-y-3">
            <legend className="block text-sm text-zinc-300">O que deseja coletar?</legend>
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
              {OPTIONS.map((option) => (
                <button
                key={option.value}
                type="button"
                onClick={() => setChoice(option.value)}
                aria-pressed={choice === option.value}
                className={cx(
                    'rounded-2xl border px-3 py-3 text-left transition-all duration-300',
                    'bg-zinc-900/70 hover:border-white/30 hover:-translate-y-0.5',
                    choice === option.value
                      ? 'border-felixo-purple/60 bg-felixo-purple/10'
                      : 'border-white/10',
                  )}
                >
                  <span className="block text-lg" aria-hidden="true">{option.icon}</span>
                  <span className={cx('mt-1 block text-sm font-medium', choice === option.value ? 'text-white' : 'text-zinc-300')}>
                    {option.label}
                  </span>
                </button>
              ))}
            </div>
          </fieldset>

          <Button type="submit" shimmer className="w-full" disabled={!isValidUrl}>
            Iniciar Coleta
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}

export default UrlInput
