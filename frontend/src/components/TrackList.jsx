import Badge from './ui/Badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card'

function extractTrackParts(trackUrl) {
  const cleaned = trackUrl.replace('https://soundcloud.com/', '')
  const [artist = '', title = ''] = cleaned.split('/')
  return { artist, title: title.replace(/-/g, ' ') }
}

function TrackList({ tracks }) {
  if (!tracks.length) return null

  return (
    <Card className="felixo-card-glow-white">
      <CardHeader className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <CardTitle className="text-lg">Faixas Encontradas</CardTitle>
          <CardDescription className="mt-1">Revise a lista antes de iniciar o download.</CardDescription>
        </div>
        <Badge className="bg-blue-500/10 text-blue-300 border-blue-500/30">
          {tracks.length} faixa(s)
        </Badge>
      </CardHeader>

      <CardContent className="p-0">
        <div className="max-h-[26rem] overflow-y-auto divide-y divide-white/5">
          {tracks.map((track, index) => {
            const { artist, title } = extractTrackParts(track)

            return (
              <div
                key={track}
                className="px-5 py-3 flex items-center gap-4 hover:bg-white/5 transition-colors duration-300"
              >
                <span className="w-8 text-right text-xs text-zinc-500 font-mono">{index + 1}</span>

                <div className="min-w-0 flex-1">
                  <p className="text-sm text-zinc-100 truncate">{title || 'Sem título'}</p>
                  <p className="text-xs text-zinc-400 truncate">{artist || 'Artista desconhecido'}</p>
                </div>

                <a
                  href={track}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-zinc-400 hover:text-felixo-purple transition-colors duration-300 text-sm"
                  aria-label={`Abrir faixa ${title || track}`}
                >
                  Abrir
                </a>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}

export default TrackList

