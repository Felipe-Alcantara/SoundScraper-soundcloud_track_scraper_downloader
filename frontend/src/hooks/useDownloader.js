import { useCallback, useRef, useState } from 'react'

/**
 * Hook para downloads via WebSocket.
 * Conecta em /api/ws/download e recebe progresso em tempo real.
 */
export function useDownloader() {
  const [status, setStatus] = useState('idle') // idle | connecting | downloading | done | error
  const [logs, setLogs] = useState([])
  const [progress, setProgress] = useState({ current: 0, total: 0, downloaded: 0, failed: 0 })
  const [currentTrack, setCurrentTrack] = useState(null)
  const wsRef = useRef(null)

  const addLog = useCallback((message) => {
    setLogs((prev) => [...prev, { time: new Date().toLocaleTimeString(), message }])
  }, [])

  const startDownload = useCallback((tracks, outputDir, format) => {
    setStatus('connecting')
    setLogs([])
    setProgress({ current: 0, total: tracks.length, downloaded: 0, failed: 0 })
    setCurrentTrack(null)

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/api/ws/download`
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      setStatus('downloading')
      addLog(`Iniciando download de ${tracks.length} faixa(s)...`)
      ws.send(JSON.stringify({ tracks, output_dir: outputDir, format }))
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      switch (data.type) {
        case 'log':
          addLog(data.message)
          break

        case 'start':
          setCurrentTrack({ index: data.index, total: data.total, url: data.url })
          setProgress((p) => ({ ...p, current: data.index }))
          addLog(data.message)
          break

        case 'complete':
          setProgress((p) => ({ ...p, current: data.index, downloaded: p.downloaded + 1 }))
          addLog(data.message)
          break

        case 'track_error':
          setProgress((p) => ({ ...p, current: data.index, failed: p.failed + 1 }))
          addLog(data.message)
          break

        case 'done':
          setStatus('done')
          setCurrentTrack(null)
          setProgress((p) => ({
            ...p,
            current: p.total,
            downloaded: data.downloaded,
            failed: data.failed,
          }))
          addLog(data.message)
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
    setLogs([])
    setProgress({ current: 0, total: 0, downloaded: 0, failed: 0 })
    setCurrentTrack(null)
  }, [])

  return { status, logs, progress, currentTrack, startDownload, reset }
}
