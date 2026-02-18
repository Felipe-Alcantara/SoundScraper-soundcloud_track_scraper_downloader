function Header() {
  return (
    <header className="border-b border-gray-800 bg-black/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-4xl mx-auto px-4 py-4 flex items-center gap-3">
        <span className="text-2xl">🎵</span>
        <h1 className="text-xl font-bold">
          Sound<span className="text-soundcloud-orange">Scraper</span>
        </h1>
        <span className="text-xs text-gray-500 ml-auto">v3.0</span>
      </div>
    </header>
  )
}

export default Header
