import Header from './components/Header'
import UrlInput from './components/UrlInput'
import TrackList from './components/TrackList'
import DownloadPanel from './components/DownloadPanel'
import DownloadProgress from './components/DownloadProgress'
import LogConsole from './components/LogConsole'
import Button from './components/ui/Button'
import Badge from './components/ui/Badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/Card'
import { useScraper } from './hooks/useScraper'
import { useDownloader } from './hooks/useDownloader'
import { cx } from './utils/cx'

const STEP_ITEMS = [
  { key: 'input', label: '1. Configurar' },
  { key: 'scraping', label: '2. Coletar' },
  { key: 'tracks', label: '3. Revisar' },
  { key: 'downloading', label: '4. Baixar' },
  { key: 'done', label: '5. Concluir' },
]

function App() {
  const scraper = useScraper()
  const downloader = useDownloader()

  const allLogs = [...scraper.logs, ...downloader.logs]

  const getStep = () => {
    if (downloader.status === 'done') return 'done'
    if (downloader.status === 'downloading' || downloader.status === 'connecting') return 'downloading'
    if (scraper.status === 'done') return 'tracks'
    if (scraper.status === 'scraping' || scraper.status === 'connecting') return 'scraping'
    if (scraper.status === 'error') return 'error'
    return 'input'
  }

  const step = getStep()

  const handleNewScrape = () => {
    scraper.reset()
    downloader.reset()
  }

  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="pointer-events-none fixed inset-0 z-0">
        <div className="absolute -top-52 left-1/2 -translate-x-1/2 w-[52rem] h-[52rem] rounded-full bg-felixo-purple/10 blur-3xl animate-gradient-orbit" />
      </div>

      <Header />

      <main className="relative z-10 max-w-7xl mx-auto w-full px-6 py-10 space-y-8">
        <section className="grid gap-8 lg:grid-cols-[1.65fr_1fr]">
          <Card className="felixo-card-glow">
            <CardHeader>
              <CardTitle className="text-2xl md:text-3xl leading-tight">
                Pipeline de Coleta e Download em Tempo Real
              </CardTitle>
              <CardDescription className="mt-2 text-sm md:text-base text-zinc-300">
                Cole a URL do SoundCloud, acompanhe eventos via WebSocket e baixe em MP3/FLAC com metadados.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-2">
                {STEP_ITEMS.map((item) => (
                  <Badge
                    key={item.key}
                    className={cx(
                      step === item.key
                        ? 'bg-felixo-purple/20 border-felixo-purple/45 text-zinc-50'
                        : 'bg-zinc-800/70 text-zinc-400 border-white/10',
                    )}
                  >
                    {item.label}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="felixo-card-glow-white">
            <CardHeader>
              <CardTitle>Status da Sessão</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-zinc-400">Coleta</span>
                <Badge className="bg-zinc-800 text-zinc-200 border-white/10">{scraper.status}</Badge>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-zinc-400">Download</span>
                <Badge className="bg-zinc-800 text-zinc-200 border-white/10">{downloader.status}</Badge>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-zinc-400">Faixas</span>
                <span className="text-zinc-100 font-mono">{scraper.tracks.length}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-zinc-400">Logs</span>
                <span className="text-zinc-100 font-mono">{allLogs.length}</span>
              </div>
            </CardContent>
          </Card>
        </section>

        {step === 'input' && (
          <UrlInput
            onScrapeStart={(url, choice) => {
              scraper.startScrape(url, choice)
            }}
          />
        )}

        {step === 'scraping' && (
          <Card className="felixo-card-glow">
            <CardContent className="py-12 flex flex-col items-center text-center gap-4">
              <div
                className="w-12 h-12 rounded-full border-2 border-felixo-purple/35 border-t-felixo-purple animate-spin"
                role="status"
                aria-label="Coleta em andamento"
              />
              <p className="text-zinc-200 text-lg text-glow">Coletando faixas do SoundCloud...</p>
              {scraper.progress.total > 0 && (
                <p className="text-sm text-zinc-400 font-mono">
                  {scraper.progress.current} / {scraper.progress.total}
                </p>
              )}
            </CardContent>
          </Card>
        )}

        {step === 'error' && (
          <Card className="border-red-500/35 bg-red-950/20" role="alert">
            <CardContent className="py-12 flex flex-col items-center text-center gap-4">
              <p className="text-red-300 text-xl">Erro durante a coleta</p>
              <Button onClick={handleNewScrape} variant="secondary">
                Tentar Novamente
              </Button>
            </CardContent>
          </Card>
        )}

        {step === 'tracks' && (
          <section className="grid gap-8 lg:grid-cols-2">
            <TrackList tracks={scraper.tracks} />
            <DownloadPanel
              tracks={scraper.tracks}
              onDownloadStart={(folder, format) => {
                downloader.startDownload(scraper.tracks, folder, format)
              }}
            />
          </section>
        )}

        {step === 'downloading' && (
          <DownloadProgress
            progress={downloader.progress}
            currentTrack={downloader.currentTrack}
          />
        )}

        {step === 'done' && (
          <Card className="felixo-card-glow">
            <CardContent className="py-12 space-y-5 text-center">
              <p className="text-2xl text-green-300 font-bold">Download concluído</p>
              <div className="text-zinc-300 space-y-1">
                <p>📥 {downloader.progress.downloaded} música(s) baixada(s)</p>
                {downloader.progress.failed > 0 && (
                  <p className="text-red-300">❌ {downloader.progress.failed} erro(s)</p>
                )}
              </div>
              <Button onClick={handleNewScrape} shimmer>
                Nova Coleta
              </Button>
            </CardContent>
          </Card>
        )}

        {allLogs.length > 0 && <LogConsole logs={allLogs} />}
      </main>
    </div>
  )
}

export default App
