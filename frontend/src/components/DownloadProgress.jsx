function DownloadProgress({ progress, currentTrack }) {
  const percent = progress.total > 0
    ? Math.round((progress.current / progress.total) * 100)
    : 0

  return (
    <div className="space-y-6 py-8">
      {/* Barra de progresso geral */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-gray-400">
          <span>Baixando faixas...</span>
          <span>{progress.current} / {progress.total}</span>
        </div>
        <div className="w-full bg-gray-800 rounded-full h-3 overflow-hidden">
          <div
            className="bg-soundcloud-orange h-full rounded-full transition-all duration-500 ease-out"
            style={{ width: `${percent}%` }}
          />
        </div>
      </div>

      {/* Faixa atual */}
      {currentTrack && (
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <p className="text-sm text-gray-400 mb-1">Baixando agora:</p>
          <p className="text-white truncate">
            {currentTrack.url.replace('https://soundcloud.com/', '')}
          </p>
          <p className="text-gray-500 text-xs mt-1">
            [{currentTrack.index}/{currentTrack.total}]
          </p>
        </div>
      )}

      {/* Contadores */}
      <div className="flex gap-6 justify-center text-sm">
        <div className="text-green-400">
          ✅ {progress.downloaded} baixada(s)
        </div>
        {progress.failed > 0 && (
          <div className="text-red-400">
            ❌ {progress.failed} erro(s)
          </div>
        )}
      </div>

      {/* Spinner */}
      <div className="flex justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-soundcloud-orange"></div>
      </div>
    </div>
  )
}

export default DownloadProgress
