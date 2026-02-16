import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { documentsService, type DocumentResponse } from '../services/documents'

export default function DocumentsPage() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuthStore()
  const [documents, setDocuments] = useState<DocumentResponse[]>([])
  const [selectedDoc, setSelectedDoc] = useState<DocumentResponse | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    loadDocuments()
  }, [isAuthenticated, navigate])

  const loadDocuments = async () => {
    try {
      const docs = await documentsService.list()
      setDocuments(docs)
    } catch (err) {
      console.error('Failed to load documents:', err)
    }
  }

  const handleGenerate = async (type: 'resume' | 'career_sheet') => {
    setIsGenerating(true)
    setError(null)
    try {
      const doc = await documentsService.generate(type)
      setDocuments((prev) => [doc, ...prev])
      setSelectedDoc(doc)
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Generation failed')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleDownloadPdf = async (doc: DocumentResponse) => {
    try {
      await documentsService.downloadPdf(doc.id, `${doc.title || 'document'}.pdf`)
    } catch {
      setError('PDF download failed')
    }
  }

  const handleDownloadDocx = async (doc: DocumentResponse) => {
    try {
      await documentsService.downloadDocx(doc.id, `${doc.title || 'document'}.docx`)
    } catch {
      setError('Word download failed')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/dashboard')} className="text-gray-500 hover:text-gray-700">
              ← 戻る
            </button>
            <h1 className="text-lg font-bold text-gray-800">書類自動生成</h1>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {/* Generate Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">📄 履歴書</h3>
            <p className="text-sm text-gray-600 mb-4">
              日本標準フォーマット（JIS規格準拠）の履歴書を自動生成します
            </p>
            <button
              onClick={() => handleGenerate('resume')}
              disabled={isGenerating}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              {isGenerating ? '生成中...' : '履歴書を生成'}
            </button>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">📋 職務経歴書</h3>
            <p className="text-sm text-gray-600 mb-4">
              職務要約・経歴詳細・スキル・自己PRを含む職務経歴書を自動生成します
            </p>
            <button
              onClick={() => handleGenerate('career_sheet')}
              disabled={isGenerating}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              {isGenerating ? '生成中...' : '職務経歴書を生成'}
            </button>
          </div>
        </div>

        {/* Loading */}
        {isGenerating && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-4 text-gray-600">AIが書類を生成中です...</p>
            <p className="mt-1 text-sm text-gray-400">30秒ほどお待ちください</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Document List */}
          <div className="lg:col-span-1">
            <h3 className="text-sm font-semibold text-gray-500 uppercase mb-3">生成済み書類</h3>
            {documents.length === 0 ? (
              <p className="text-sm text-gray-400">まだ書類がありません</p>
            ) : (
              <div className="space-y-2">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    onClick={() => setSelectedDoc(doc)}
                    className={`bg-white rounded-lg border p-3 cursor-pointer transition-colors ${
                      selectedDoc?.id === doc.id ? 'border-blue-500 ring-1 ring-blue-500' : 'hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-sm text-gray-800">
                        {doc.title || doc.document_type}
                      </span>
                      <span className="text-xs text-gray-400">
                        {new Date(doc.generated_at).toLocaleDateString('ja-JP')}
                      </span>
                    </div>
                    <div className="flex gap-2 mt-2">
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDownloadPdf(doc); }}
                        className="text-xs bg-red-50 text-red-600 hover:bg-red-100 px-2 py-1 rounded transition-colors"
                      >
                        PDF
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDownloadDocx(doc); }}
                        className="text-xs bg-blue-50 text-blue-600 hover:bg-blue-100 px-2 py-1 rounded transition-colors"
                      >
                        Word
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Preview */}
          <div className="lg:col-span-2">
            <h3 className="text-sm font-semibold text-gray-500 uppercase mb-3">プレビュー</h3>
            {selectedDoc?.content_html ? (
              <div className="bg-white rounded-lg border shadow-sm">
                <div className="flex items-center justify-between p-3 border-b bg-gray-50 rounded-t-lg">
                  <span className="text-sm font-medium text-gray-700">{selectedDoc.title}</span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleDownloadPdf(selectedDoc)}
                      className="text-xs bg-red-600 text-white hover:bg-red-700 px-3 py-1 rounded transition-colors"
                    >
                      PDF ダウンロード
                    </button>
                    <button
                      onClick={() => handleDownloadDocx(selectedDoc)}
                      className="text-xs bg-blue-600 text-white hover:bg-blue-700 px-3 py-1 rounded transition-colors"
                    >
                      Word ダウンロード
                    </button>
                  </div>
                </div>
                <div
                  className="p-6 overflow-auto max-h-[800px]"
                  dangerouslySetInnerHTML={{ __html: selectedDoc.content_html }}
                />
              </div>
            ) : (
              <div className="bg-white rounded-lg border p-12 text-center text-gray-400">
                <p>書類を選択するか、新しく生成してください</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
