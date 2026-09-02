import { useState } from 'react'
import Button from './ui/Button'
import Input from './ui/Input'
import Badge from './ui/Badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card'
import { cx } from '../utils/cx'
import { buildApiUrl } from '../utils/network'

const FORMATS = [
  { value: 'flac', label: 'FLAC', subtitle: 'Lossless', icon: '🎼' },
  { value: 'mp3', label: 'MP3', subtitle: '320kbps', icon: '🎧' },
]

function DownloadPanel({ tracks, onDownloadStart }) {
  const [format, setFormat] = useState('flac')
  const [folder, setFolder] = useState('')
  const [folderError, setFolderError] = useState('')

  const handleSelectFolder = async () => {
    setFolderError('')
    try {
      const response = await fetch(buildApiUrl('/api/select-folder'), { method: 'POST' })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const data = await response.json()
      if (data.success) {
        setFolder(data.path)
      } else {
        setFolderError(data.message || 'Nenhuma pasta foi selecionada.')
      }
    } catch {
      setFolderError('Não foi possível abrir o seletor de pastas. Tente novamente.')
    }
  }

  const handleDownload = () => {
    if (!folder) return
    onDownloadStart(folder, format)
  }

  return (
    <Card className="felixo-card-glow">
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <CardTitle className="text-lg">Configuração de Download</CardTitle>
            <CardDescription className="mt-1">
              Escolha formato e pasta de destino para iniciar o processamento.
            </CardDescription>
          </div>
          <Badge className="bg-green-950/80 text-green-300 border-green-700/60">
            Etapa 2
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <fieldset className="space-y-2">
          <legend className="block text-sm text-zinc-300">Formato de áudio</legend>
          <div className="grid sm:grid-cols-2 gap-3">
            {FORMATS.map((item) => (
              <button
                key={item.value}
                type="button"
                onClick={() => setFormat(item.value)}
                aria-pressed={format === item.value}
                className={cx(
                  'rounded-2xl border p-4 text-left transition-all duration-300',
                  'hover:-translate-y-0.5 hover:border-white/30',
                  format === item.value
                    ? 'border-felixo-purple/60 bg-felixo-purple/10'
                    : 'border-white/10 bg-zinc-900/60',
                )}
              >
                <span className="block text-xl" aria-hidden="true">{item.icon}</span>
                <span className="mt-2 block font-semibold">{item.label}</span>
                <span className="text-xs text-zinc-400">{item.subtitle}</span>
              </button>
            ))}
          </div>
        </fieldset>

        <div className="space-y-2">
          <label htmlFor="download-folder" className="block text-sm text-zinc-300">
            Pasta de destino
          </label>
          <div className="flex flex-col sm:flex-row gap-3">
            <Input
              id="download-folder"
              value={folder}
              readOnly
              placeholder="Nenhuma pasta selecionada"
              className="flex-1"
            />
            <Button type="button" variant="secondary" onClick={handleSelectFolder}>
              Escolher Pasta
            </Button>
          </div>
          {folderError && <p className="text-xs text-red-300" role="alert">{folderError}</p>}
        </div>

        <Button
          type="button"
          onClick={handleDownload}
          disabled={!folder}
          shimmer
          className="w-full"
        >
          Baixar {tracks.length} faixa(s) em {format.toUpperCase()}
        </Button>
      </CardContent>
    </Card>
  )
}

export default DownloadPanel
