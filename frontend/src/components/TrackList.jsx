function TrackList({ tracks }) {
  if (!tracks.length) return null

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">
          🎵 Faixas encontradas ({tracks.length})
        </h2>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-lg divide-y divide-gray-800 max-h-96 overflow-y-auto">
        {tracks.map((track, i) => {
          // Extrai nome legível da URL
          const parts = track.replace('https://soundcloud.com/', '').split('/')
          const artist = parts[0] || ''
          const title = parts[1] || ''

          return (
            <div
              key={track}
              className="flex items-center gap-3 px-4 py-3 hover:bg-gray-800/50 transition"
            >
              <span className="text-gray-600 text-sm w-8 text-right">{i + 1}</span>
              <div className="flex-1 min-w-0">
                <p className="text-white truncate">{title.replace(/-/g, ' ')}</p>
                <p className="text-gray-500 text-sm truncate">{artist}</p>
              </div>
              <a
                href={track}
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-500 hover:text-soundcloud-orange transition text-sm"
              >
                🔗
              </a>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default TrackList
