import Header from './components/Header'
import UrlInput from './components/UrlInput'
import TrackList from './components/TrackList'
import DownloadPanel from './components/DownloadPanel'
import DownloadProgress from './components/DownloadProgress'
import LogConsole from './components/LogConsole'
import { useScraper } from './hooks/useScraper'
import { useDownloader } from './hooks/useDownloader'

/**
 * SoundScraper — App principal
 * 
 * Fluxo completo conectado via WebSocket:
 *  1. Usuário cola a URL → escolhe opção → clica Buscar
 *  2. WebSocket /ws/scrape envia eventos em tempo real
 *  3. Lista de faixas renderizada com checkboxes
 *  4. Escolhe formato + pasta → inicia download via /ws/download
 *  5. Progresso por faixa em tempo real
 */
function App() {
  const scraper = useScraper()
  const downloader = useDownloader()

  // Combina logs do scraper e downloader
  const allLogs = [...scraper.logs, ...downloader.logs]

  // Determina o step atual
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
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 max-w-4xl mx-auto w-full px-4 py-8 space-y-6">
        {/* Etapa 1: Input da URL */}
        {step === 'input' && (
          <UrlInput
            onScrapeStart={(url, choice) => {
              scraper.startScrape(url, choice)
            }}
          />
        )}

        {/* Etapa 2: Scraping em andamento */}
        {step === 'scraping' && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-soundcloud-orange mx-auto mb-4"></div>
            <p className="text-gray-400">Coletando faixas do SoundCloud...</p>
            {scraper.progress.total > 0 && (
              <p className="text-gray-500 text-sm mt-2">
                {scraper.progress.current} / {scraper.progress.total} faixas
              </p>
            )}
          </div>
        )}

        {/* Etapa 2b: Erro no scraping */}
        {step === 'error' && (
          <div className="text-center py-12">
            <p className="text-red-400 text-xl mb-4">❌ Erro na coleta</p>
            <button
              onClick={handleNewScrape}
              className="bg-soundcloud-orange hover:bg-orange-600 text-white px-6 py-2 rounded-lg transition"
            >
              Tentar novamente
            </button>
          </div>
        )}

        {/* Etapa 3: Lista de faixas + painel de download */}
        {step === 'tracks' && (
          <>
            <TrackList tracks={scraper.tracks} />
            <DownloadPanel
              tracks={scraper.tracks}
              onDownloadStart={(folder, format) => {
                downloader.startDownload(scraper.tracks, folder, format)
              }}
            />
          </>
        )}

        {/* Etapa 4: Download em andamento */}
        {step === 'downloading' && (
          <DownloadProgress progress={downloader.progress} currentTrack={downloader.currentTrack} />
        )}

        {/* Etapa 5: Concluído */}
        {step === 'done' && (
          <div className="text-center py-12 space-y-4">
            <p className="text-green-400 text-2xl">✅ Download concluído!</p>
            <div className="text-gray-400">
              <p>📥 {downloader.progress.downloaded} música(s) baixada(s)</p>
              {downloader.progress.failed > 0 && (
                <p className="text-red-400">❌ {downloader.progress.failed} erro(s)</p>
              )}
            </div>
            <button
              onClick={handleNewScrape}
              className="bg-soundcloud-orange hover:bg-orange-600 text-white px-6 py-2 rounded-lg transition"
            >
              Nova coleta
            </button>
          </div>
        )}

        {/* Console de logs (sempre visível quando há logs) */}
        {allLogs.length > 0 && <LogConsole logs={allLogs} />}
      </main>
    </div>
  )
}

export default App
