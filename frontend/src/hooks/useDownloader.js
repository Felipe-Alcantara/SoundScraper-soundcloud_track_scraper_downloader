import { useCallback, useRef, useState } from 'react'
import { API_ORIGIN, buildApiUrl, buildWsUrl } from '../utils/network'

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
  const closedManuallyRef = useRef(false)
  const terminalEventReceivedRef = useRef(false)

  const addLog = useCallback((message) => {
    setLogs((prev) => [...prev, { time: new Date().toLocaleTimeString(), message }])
  }, [])

  const startDownload = useCallback((tracks, outputDir, format) => {
    closedManuallyRef.current = false
    terminalEventReceivedRef.current = false
    setStatus('connecting')
    setLogs([])
    setProgress({ current: 0, total: tracks.length, downloaded: 0, failed: 0 })
    setCurrentTrack(null)

    const connect = async () => {
      try {
        const response = await fetch(buildApiUrl('/api/info'), { method: 'GET' })
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
      } catch {
        setStatus('error')
        addLog(`❌ Backend indisponível em ${API_ORIGIN}`)
        addLog('⚠️ Inicie o backend antes de baixar faixas')
        return
      }

      const wsUrl = buildWsUrl('/api/ws/download')
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setStatus('downloading')
        addLog(`Conectado em ${wsUrl}`)
        addLog(`Iniciando download de ${tracks.length} faixa(s)...`)
        ws.send(JSON.stringify({ tracks, output_dir: outputDir, format }))
      }

      ws.onmessage = (event) => {
        let data
        try {
          data = JSON.parse(event.data)
        } catch {
          setStatus('error')
          addLog('❌ Mensagem inválida recebida do servidor de download')
          return
        }

        switch (data.type) {
          case 'log':
            addLog(data.message)
            break

          case 'start':
            setCurrentTrack({ index: data.index, total: data.total, url: data.url })
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
            terminalEventReceivedRef.current = true
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
            terminalEventReceivedRef.current = true
            setStatus('error')
            addLog(`❌ ${data.message}`)
            break

          default:
            addLog(data.message || JSON.stringify(data))
        }
      }

      ws.onerror = () => {
        setStatus('error')
        addLog(`❌ Erro na conexão WebSocket (${wsUrl})`)
      }

      ws.onclose = () => {
        if (wsRef.current === ws) {
          wsRef.current = null
        }

        if (!closedManuallyRef.current && !terminalEventReceivedRef.current) {
          setStatus((prev) => {
            if (prev === 'done' || prev === 'error' || prev === 'idle') {
              return prev
            }
            return 'error'
          })
          addLog('⚠️ Conexão WebSocket encerrada antes da conclusão do download')
        }
      }
    }

    void connect()
  }, [addLog])

  const reset = useCallback(() => {
    if (wsRef.current) {
      closedManuallyRef.current = true
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
