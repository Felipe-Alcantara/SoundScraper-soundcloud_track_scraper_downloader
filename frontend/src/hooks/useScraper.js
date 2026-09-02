import { useCallback, useRef, useState } from 'react'
import { API_ORIGIN, buildApiUrl, buildWsUrl } from '../utils/network'

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
  const closedManuallyRef = useRef(false)
  const terminalEventReceivedRef = useRef(false)

  const addLog = useCallback((message) => {
    setLogs((prev) => [...prev, { time: new Date().toLocaleTimeString(), message }])
  }, [])

  const startScrape = useCallback((url, choice) => {
    closedManuallyRef.current = false
    terminalEventReceivedRef.current = false
    setStatus('connecting')
    setTracks([])
    setLogs([])
    setProgress({ current: 0, total: 0 })

    const connect = async () => {
      try {
        const response = await fetch(buildApiUrl('/api/info'), { method: 'GET' })
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
      } catch {
        setStatus('error')
        addLog(`❌ Backend indisponível em ${API_ORIGIN}`)
        addLog('⚠️ Inicie o backend antes de coletar faixas')
        return
      }

      const wsUrl = buildWsUrl('/api/ws/scrape')
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setStatus('scraping')
        addLog(`Conectado em ${wsUrl}`)
        addLog(`Conectado! Iniciando coleta de ${url}...`)
        ws.send(JSON.stringify({ url, choice }))
      }

      ws.onmessage = (event) => {
        let data
        try {
          data = JSON.parse(event.data)
        } catch {
          setStatus('error')
          addLog('❌ Mensagem inválida recebida do servidor de scraping')
          return
        }

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
            terminalEventReceivedRef.current = true
            setStatus('done')
            setTracks(data.tracks || [])
            setProgress({ current: data.total, total: data.total })
            addLog(data.message || `Concluído: ${data.total} faixa(s)`)
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
          addLog('⚠️ Conexão WebSocket encerrada antes da conclusão da coleta')
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
    setTracks([])
    setLogs([])
    setProgress({ current: 0, total: 0 })
  }, [])

  return { status, tracks, logs, progress, startScrape, reset }
}
