import { useCallback, useRef, useState } from 'react'

/**
 * Hook para scraping via WebSocket.
 * Conecta em /api/ws/scrape e recebe eventos em tempo real.
 */
export function useScraper() {
  const [status, setStatus] = useState('idle') // idle | connecting | scraping | done | error
  const [tracks, setTracks] = useState([])
  const [logs, setLogs] = useState([])
  const [progress, setProgress] = useState({ current: 0, total: 0 })
  const wsRef = useRef(null)

  const addLog = useCallback((message) => {
    setLogs((prev) => [...prev, { time: new Date().toLocaleTimeString(), message }])
  }, [])

  const startScrape = useCallback((url, choice) => {
    setStatus('connecting')
    setTracks([])
    setLogs([])
    setProgress({ current: 0, total: 0 })

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/api/ws/scrape`
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      setStatus('scraping')
      addLog(`Conectado! Iniciando coleta de ${url}...`)
      ws.send(JSON.stringify({ url, choice }))
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      switch (data.type) {
        case 'log':
          addLog(data.message)
          break

        case 'stage':
          addLog(`── ${data.message}`)
          break

        case 'track':
          setTracks((prev) => [...prev, data.url])
          setProgress({ current: data.index, total: data.total })
          break

        case 'done':
          setStatus('done')
          setTracks(data.tracks || [])
          setProgress({ current: data.total, total: data.total })
          addLog(data.message || `Concluído: ${data.total} faixa(s)`)
          break

        case 'error':
          setStatus('error')
          addLog(`❌ ${data.message}`)
          break

        default:
          addLog(data.message || JSON.stringify(data))
      }
    }

    ws.onerror = () => {
      setStatus('error')
      addLog('Erro na conexão WebSocket')
    }

    ws.onclose = () => {
      if (wsRef.current === ws) {
        wsRef.current = null
      }
    }
  }, [addLog])

  const reset = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setStatus('idle')
    setTracks([])
    setLogs([])
    setProgress({ current: 0, total: 0 })
  }, [])

  return { status, tracks, logs, progress, startScrape, reset }
}
