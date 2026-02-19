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

  const handleSelectFolder = async () => {
    try {
      const response = await fetch(buildApiUrl('/api/select-folder'), { method: 'POST' })
      const data = await response.json()
      if (data.success) {
        setFolder(data.path)
      }
    } catch (error) {
      console.error('Erro ao selecionar pasta:', error)
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
        <div className="space-y-2">
          <label className="block text-sm text-zinc-300">Formato de áudio</label>
          <div className="grid sm:grid-cols-2 gap-3">
            {FORMATS.map((item) => (
              <button
                key={item.value}
                type="button"
                onClick={() => setFormat(item.value)}
                className={cx(
                  'rounded-2xl border p-4 text-left transition-all duration-300',
                  'hover:-translate-y-0.5 hover:border-white/30',
                  format === item.value
                    ? 'border-felixo-purple/60 bg-felixo-purple/10'
                    : 'border-white/10 bg-zinc-900/60',
                )}
              >
                <span className="block text-xl">{item.icon}</span>
                <span className="mt-2 block font-semibold">{item.label}</span>
                <span className="text-xs text-zinc-400">{item.subtitle}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <label className="block text-sm text-zinc-300">Pasta de destino</label>
          <div className="flex flex-col sm:flex-row gap-3">
            <Input
              value={folder}
              readOnly
              placeholder="Nenhuma pasta selecionada"
              className="flex-1"
            />
            <Button type="button" variant="secondary" onClick={handleSelectFolder}>
              Escolher Pasta
            </Button>
          </div>
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
