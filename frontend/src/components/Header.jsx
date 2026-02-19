import Badge from './ui/Badge'

function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-black/70 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-4">
        <div className="h-11 w-11 rounded-2xl border border-felixo-purple/40 bg-zinc-900/90 flex items-center justify-center text-xl">
          🎵
        </div>

        <div>
          <p className="text-[11px] uppercase tracking-[0.22em] text-zinc-500">
            SoundCloud Downloader
          </p>
          <h1 className="text-2xl md:text-3xl font-bold leading-tight">
            Sound<span className="text-felixo-purple title-glow-purple">Scraper</span>
          </h1>
        </div>

        <Badge className="ml-auto bg-felixo-purple/10 text-felixo-purple border-felixo-purple/35">
          v3.0 Web
        </Badge>
      </div>
    </header>
  )
}

export default Header
