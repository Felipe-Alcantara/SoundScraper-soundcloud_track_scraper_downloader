import { useState } from 'react'

function DownloadPanel({ tracks, onDownloadStart }) {
  const [format, setFormat] = useState('flac')
  const [folder, setFolder] = useState('')

  const handleSelectFolder = async () => {
    try {
      const res = await fetch('/api/select-folder', { method: 'POST' })
      const data = await res.json()
      if (data.success) {
        setFolder(data.path)
      }
    } catch (err) {
      console.error('Erro ao selecionar pasta:', err)
    }
  }

  const handleDownload = () => {
    if (!folder) return
    onDownloadStart(folder, format)
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-5">
      <h2 className="text-lg font-semibold">⬇️ Download</h2>

      {/* Formato */}
      <div>
        <label className="block text-sm text-gray-400 mb-2">Formato de áudio</label>
        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => setFormat('flac')}
            className={`flex-1 py-3 rounded-lg border transition text-center
              ${format === 'flac'
                ? 'border-soundcloud-orange bg-soundcloud-orange/10 text-white'
                : 'border-gray-700 bg-gray-800 text-gray-400 hover:border-gray-500'
              }`}
          >
            <span className="block text-lg">🎼</span>
            <span className="font-semibold">FLAC</span>
            <span className="block text-xs text-gray-500">Lossless</span>
          </button>
          <button
            type="button"
            onClick={() => setFormat('mp3')}
            className={`flex-1 py-3 rounded-lg border transition text-center
              ${format === 'mp3'
                ? 'border-soundcloud-orange bg-soundcloud-orange/10 text-white'
                : 'border-gray-700 bg-gray-800 text-gray-400 hover:border-gray-500'
              }`}
          >
            <span className="block text-lg">🎧</span>
            <span className="font-semibold">MP3</span>
            <span className="block text-xs text-gray-500">320kbps</span>
          </button>
        </div>
      </div>

      {/* Pasta */}
      <div>
        <label className="block text-sm text-gray-400 mb-2">Pasta de destino</label>
        <div className="flex gap-2">
          <input
            type="text"
            value={folder}
            readOnly
            placeholder="Nenhuma pasta selecionada..."
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white
                       placeholder-gray-500 text-sm"
          />
          <button
            type="button"
            onClick={handleSelectFolder}
            className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition text-sm"
          >
            📂 Escolher
          </button>
        </div>
      </div>

      {/* Botão download */}
      <button
        type="button"
        onClick={handleDownload}
        disabled={!folder}
        className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-700

                   disabled:text-gray-500 text-white font-semibold py-3 rounded-lg
                   transition"
      >
        ⬇️ Baixar {tracks.length} faixa(s) em {format.toUpperCase()}
      </button>
    </div>
  )
}

export default DownloadPanel
