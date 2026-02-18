import { useState } from 'react'

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

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!url.trim()) return
    onScrapeStart(url.trim(), choice)
  }

  const isValidUrl = url.includes('soundcloud.com/') || url.match(/^[a-zA-Z0-9_-]+$/)

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Input da URL */}
      <div>
        <label className="block text-sm text-gray-400 mb-2">
          Link do SoundCloud
        </label>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="soundcloud.com/artista ou cole o link completo..."
          className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white
                     placeholder-gray-500 focus:outline-none focus:border-soundcloud-orange
                     transition"
        />
      </div>

      {/* Opções */}
      <div>
        <label className="block text-sm text-gray-400 mb-3">
          O que deseja baixar?
        </label>
        <div className="grid grid-cols-4 sm:grid-cols-7 gap-2">
          {OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => setChoice(opt.value)}
              className={`flex flex-col items-center gap-1 py-3 px-2 rounded-lg border transition text-sm
                ${choice === opt.value
                  ? 'border-soundcloud-orange bg-soundcloud-orange/10 text-white'
                  : 'border-gray-700 bg-gray-900 text-gray-400 hover:border-gray-500'
                }`}
            >
              <span className="text-lg">{opt.icon}</span>
              <span>{opt.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Botão de iniciar */}
      <button
        type="submit"
        disabled={!isValidUrl}
        className="w-full bg-soundcloud-orange hover:bg-orange-600 disabled:bg-gray-700
                   disabled:text-gray-500 text-white font-semibold py-3 rounded-lg
                   transition"
      >
        🔍 Buscar faixas
      </button>
    </form>
  )
}

export default UrlInput
