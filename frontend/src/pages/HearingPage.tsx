import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { hearingService } from '../services/hearing'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const STEP_LABELS = ['', '自己紹介', '職務経歴', 'スキル・資格', '希望条件', '転職理由・ビジョン']

export default function HearingPage() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuthStore()
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [currentStep, setCurrentStep] = useState(1)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingText, setStreamingText] = useState('')
  const [isCompleted, setIsCompleted] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    initSession()
  }, [isAuthenticated, navigate])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingText])

  const initSession = async () => {
    try {
      const data = await hearingService.startSession()
      setSessionId(data.session_id)
      setCurrentStep(data.current_step)
      setMessages([{ role: 'assistant', content: data.greeting }])
    } catch (err) {
      setError('セッションの開始に失敗しました')
      console.error(err)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || !sessionId || isStreaming) return

    const userMessage = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }])
    setIsStreaming(true)
    setStreamingText('')
    setError(null)

    hearingService.streamMessage(
      sessionId,
      userMessage,
      (chunk) => {
        setStreamingText((prev) => prev + chunk)
      },
      (data) => {
        setStreamingText((prev) => {
          // Move streaming text to messages
          setMessages((msgs) => [...msgs, { role: 'assistant', content: prev }])
          return ''
        })
        setCurrentStep(data.current_step)
        setIsStreaming(false)
      },
      (errMsg) => {
        setError(errMsg)
        setIsStreaming(false)
        setStreamingText('')
      },
    )
  }

  const handleNextStep = async () => {
    if (!sessionId) return
    try {
      const session = await hearingService.advanceStep(sessionId)
      setCurrentStep(session.current_step)
      if (session.is_completed) {
        setIsCompleted(true)
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: 'ヒアリングが完了しました！お話いただいた内容を基に、プロフィールを保存しました。次は「書類生成」で履歴書・職務経歴書を作成しましょう。',
          },
        ])
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: `ステップ${session.current_step}「${STEP_LABELS[session.current_step]}」に進みます。続けてお聞かせください。`,
          },
        ])
      }
    } catch (err) {
      setError('ステップの進行に失敗しました')
      console.error(err)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-3 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="text-gray-500 hover:text-gray-700"
            >
              ← 戻る
            </button>
            <h1 className="text-lg font-bold text-gray-800">AIヒアリング</h1>
          </div>

          {/* Step Progress */}
          <div className="flex items-center gap-1">
            {[1, 2, 3, 4, 5].map((step) => (
              <div key={step} className="flex items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium ${
                    step < currentStep
                      ? 'bg-green-500 text-white'
                      : step === currentStep
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                >
                  {step < currentStep ? '✓' : step}
                </div>
                {step < 5 && (
                  <div className={`w-4 h-0.5 ${step < currentStep ? 'bg-green-500' : 'bg-gray-200'}`} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Step label */}
        <div className="max-w-4xl mx-auto px-4 pb-2">
          <p className="text-sm text-gray-500">
            Step {currentStep}: {STEP_LABELS[currentStep]}
            {isCompleted && ' (完了)'}
          </p>
        </div>
      </header>

      {/* Chat Messages */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6 space-y-4">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-[80%] rounded-lg px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-gray-200 text-gray-800'
                }`}
              >
                {msg.role === 'assistant' && (
                  <div className="text-xs text-gray-400 mb-1">🤖 KiraAI</div>
                )}
                <div className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</div>
              </div>
            </div>
          ))}

          {/* Streaming response */}
          {isStreaming && streamingText && (
            <div className="flex justify-start">
              <div className="max-w-[80%] rounded-lg px-4 py-3 bg-white border border-gray-200 text-gray-800">
                <div className="text-xs text-gray-400 mb-1">🤖 KiraAI</div>
                <div className="whitespace-pre-wrap text-sm leading-relaxed">{streamingText}</div>
                <span className="inline-block w-2 h-4 bg-blue-500 animate-pulse ml-1" />
              </div>
            </div>
          )}

          {/* Loading indicator */}
          {isStreaming && !streamingText && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input Area */}
      <footer className="bg-white border-t">
        <div className="max-w-4xl mx-auto px-4 py-3">
          {!isCompleted ? (
            <div className="flex gap-2">
              <div className="flex-1 flex gap-2">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="メッセージを入力..."
                  rows={1}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none"
                  disabled={isStreaming}
                />
                <button
                  onClick={sendMessage}
                  disabled={!input.trim() || isStreaming}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-lg transition-colors"
                >
                  送信
                </button>
              </div>
              {!isStreaming && messages.length > 1 && (
                <button
                  onClick={handleNextStep}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg transition-colors whitespace-nowrap"
                >
                  {currentStep >= 5 ? '完了' : `次へ (Step ${currentStep + 1})`}
                </button>
              )}
            </div>
          ) : (
            <div className="flex gap-2 justify-center">
              <button
                onClick={() => navigate('/dashboard')}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                ダッシュボードに戻る
              </button>
            </div>
          )}
        </div>
      </footer>
    </div>
  )
}
