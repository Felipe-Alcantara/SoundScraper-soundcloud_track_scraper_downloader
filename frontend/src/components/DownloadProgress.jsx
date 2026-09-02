import Badge from './ui/Badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card'

function DownloadProgress({ progress, currentTrack }) {
  const percent = progress.total > 0
    ? Math.round((progress.current / progress.total) * 100)
    : 0

  return (
    <Card className="felixo-card-glow">
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <CardTitle className="text-lg">Download em Andamento</CardTitle>
            <CardDescription className="mt-1">
              Progresso em tempo real do processamento das faixas.
            </CardDescription>
          </div>
          <Badge className="bg-yellow-400/20 text-yellow-100 border-yellow-400/40">
            {percent}%
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-zinc-400 font-mono">
            <span>Faixas concluídas</span>
            <span>{progress.current} / {progress.total}</span>
          </div>
          <div className="h-3 rounded-full bg-zinc-800 overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-felixo-purple to-felixo-purple-bright transition-all duration-500 ease-out"
              style={{ width: `${percent}%` }}
              role="progressbar"
              aria-label="Progresso do download"
              aria-valuemin="0"
              aria-valuemax="100"
              aria-valuenow={percent}
            />
          </div>
        </div>

        {currentTrack && (
          <div className="rounded-2xl border border-white/10 bg-zinc-900/70 p-4">
            <p className="text-xs text-zinc-400">Faixa atual</p>
            <p className="mt-1 text-sm text-zinc-100 truncate">
              {currentTrack.url.replace('https://soundcloud.com/', '')}
            </p>
            <p className="mt-1 text-xs text-zinc-500 font-mono">
              [{currentTrack.index}/{currentTrack.total}]
            </p>
          </div>
        )}

        <div className="flex flex-wrap gap-3">
          <Badge className="bg-green-950/80 text-green-300 border-green-700/60">
            ✅ {progress.downloaded} baixada(s)
          </Badge>
          {progress.failed > 0 && (
            <Badge className="bg-red-950/80 text-red-300 border-red-700/60">
              ❌ {progress.failed} erro(s)
            </Badge>
          )}
        </div>

        <div className="w-8 h-8 rounded-full border-2 border-felixo-purple/35 border-t-felixo-purple animate-spin" />
      </CardContent>
    </Card>
  )
}

export default DownloadProgress
