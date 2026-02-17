import api from './api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface HearingStartResponse {
  session_id: string
  current_step: number
  step_title: string
  greeting: string
}

export interface HearingSession {
  id: string
  current_step: number
  conversation_log: Array<{ role: string; content: string }>
  extracted_data: Record<string, unknown>
  is_completed: boolean
  created_at: string
}

export const hearingService = {
  async startSession(): Promise<HearingStartResponse> {
    const response = await api.post<HearingStartResponse>('/hearing/start')
    return response.data
  },

  async getSession(sessionId: string): Promise<HearingSession> {
    const response = await api.get<HearingSession>(`/hearing/session/${sessionId}`)
    return response.data
  },

  async advanceStep(sessionId: string): Promise<HearingSession> {
    const response = await api.post<HearingSession>(`/hearing/session/${sessionId}/next-step`)
    return response.data
  },

  streamMessage(
    sessionId: string,
    message: string,
    onChunk: (text: string) => void,
    onDone: (data: { current_step: number; step_title: string; extracted_data: unknown }) => void,
    onError: (error: string) => void,
  ): () => void {
    const token = localStorage.getItem('access_token')
    const params = new URLSearchParams({
      session_id: sessionId,
      message: message,
    })

    const url = `${API_BASE_URL}/api/hearing/stream?${params.toString()}`

    // EventSource doesn't support custom headers, so we use fetch with SSE parsing instead
    const abortController = new AbortController()

    fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      signal: abortController.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`HTTP error ${response.status}`)
        }

        const reader = response.body?.getReader()
        if (!reader) throw new Error('No reader')

        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })

          // Parse SSE events
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))
                if (data.type === 'chunk') {
                  onChunk(data.content)
                } else if (data.type === 'done') {
                  onDone(data)
                } else if (data.type === 'error') {
                  onError(data.message)
                }
              } catch {
                // Skip malformed JSON
              }
            }
          }
        }
      })
      .catch((err) => {
        if (err.name !== 'AbortError') {
          onError(err.message || 'Stream failed')
        }
      })

    return () => {
      abortController.abort()
    }
  },
}
