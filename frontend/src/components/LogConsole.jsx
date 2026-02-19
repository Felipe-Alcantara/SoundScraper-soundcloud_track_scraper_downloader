import { useEffect, useRef } from 'react'
import Badge from './ui/Badge'
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card'

function LogConsole({ logs }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  return (
    <Card className="felixo-card-glow-white">
      <CardHeader className="flex items-center justify-between gap-3">
        <CardTitle className="text-sm">Console em Tempo Real</CardTitle>
        <Badge className="bg-zinc-800 text-zinc-300 border-white/10">
          {logs.length} evento(s)
        </Badge>
      </CardHeader>

      <CardContent className="p-0">
        <div className="max-h-56 overflow-y-auto font-mono text-xs">
          {logs.map((log, index) => (
            <div key={`${log.time}-${index}`} className="px-5 py-2 border-b border-white/5 flex gap-3">
              <span className="text-zinc-500 shrink-0">[{log.time}]</span>
              <span className="text-zinc-300 break-words">{log.message}</span>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
      </CardContent>
    </Card>
  )
}

export default LogConsole

