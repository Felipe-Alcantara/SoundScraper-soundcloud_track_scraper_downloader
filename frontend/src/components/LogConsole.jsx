import { useEffect, useRef } from 'react'

function LogConsole({ logs }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  return (
    <div className="bg-black border border-gray-800 rounded-lg overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-2 bg-gray-900 border-b border-gray-800">
        <span className="text-xs text-gray-500">📋 Console</span>
      </div>
      <div className="p-4 max-h-48 overflow-y-auto font-mono text-xs space-y-1">
        {logs.map((log, i) => (
          <div key={i} className="flex gap-2">
            <span className="text-gray-600 select-none">[{log.time}]</span>
            <span className="text-gray-300">{log.message}</span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}

export default LogConsole
