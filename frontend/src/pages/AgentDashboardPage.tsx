import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { agentService, type AgentDashboard } from '../services/agent'

export default function AgentDashboardPage() {
  const navigate = useNavigate()
  const [dashboard, setDashboard] = useState<AgentDashboard | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [editForm, setEditForm] = useState({
    company_name: '',
    description: '',
    website_url: '',
  })
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      const data = await agentService.getDashboard()
      setDashboard(data)
      setEditForm({
        company_name: data.profile.company_name,
        description: data.profile.description || '',
        website_url: data.profile.website_url || '',
      })
    } catch {
      setError('ダッシュボードの読み込みに失敗しました')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSave = async () => {
    setIsSaving(true)
    setError(null)
    try {
      await agentService.updateProfile(editForm)
      setSuccess('保存しました')
      setIsEditing(false)
      loadDashboard()
      setTimeout(() => setSuccess(null), 3000)
    } catch {
      setError('保存に失敗しました')
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
      </div>
    )
  }

  const planLabels: Record<string, string> = {
    basic: 'ベーシック',
    standard: 'スタンダード',
    premium: 'プレミアム',
    custom: 'カスタム',
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/dashboard')} className="text-gray-500 hover:text-gray-700">
              ← 戻る
            </button>
            <h1 className="text-lg font-bold text-gray-800">エージェント管理</h1>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}
        {success && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
            <p className="text-green-700 text-sm">{success}</p>
          </div>
        )}

        {dashboard && (
          <>
            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-white rounded-lg shadow-sm border p-4">
                <p className="text-sm text-gray-500">プラン</p>
                <p className="text-xl font-bold text-orange-600">
                  {planLabels[dashboard.stats.plan] || dashboard.stats.plan}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow-sm border p-4">
                <p className="text-sm text-gray-500">ページ閲覧数</p>
                <p className="text-xl font-bold text-gray-800">{dashboard.stats.page_views}</p>
              </div>
              <div className="bg-white rounded-lg shadow-sm border p-4">
                <p className="text-sm text-gray-500">プロフィール閲覧数</p>
                <p className="text-xl font-bold text-gray-800">{dashboard.stats.profile_views}</p>
              </div>
              <div className="bg-white rounded-lg shadow-sm border p-4">
                <p className="text-sm text-gray-500">お問い合わせ</p>
                <p className="text-xl font-bold text-gray-800">{dashboard.stats.inquiries}</p>
              </div>
            </div>

            {/* Profile */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-800">掲載情報</h2>
                {!isEditing ? (
                  <button
                    onClick={() => setIsEditing(true)}
                    className="text-sm bg-orange-600 hover:bg-orange-700 text-white px-4 py-1.5 rounded-lg transition-colors"
                  >
                    編集
                  </button>
                ) : (
                  <div className="flex gap-2">
                    <button
                      onClick={() => setIsEditing(false)}
                      className="text-sm bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-1.5 rounded-lg transition-colors"
                    >
                      キャンセル
                    </button>
                    <button
                      onClick={handleSave}
                      disabled={isSaving}
                      className="text-sm bg-orange-600 hover:bg-orange-700 disabled:bg-orange-400 text-white px-4 py-1.5 rounded-lg transition-colors"
                    >
                      {isSaving ? '保存中...' : '保存'}
                    </button>
                  </div>
                )}
              </div>

              {!isEditing ? (
                <dl className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <dt className="text-gray-500">会社名</dt>
                    <dd className="text-gray-800 font-medium mt-1">{dashboard.profile.company_name}</dd>
                  </div>
                  <div>
                    <dt className="text-gray-500">Webサイト</dt>
                    <dd className="text-gray-800 font-medium mt-1">{dashboard.profile.website_url || '未設定'}</dd>
                  </div>
                  <div className="md:col-span-2">
                    <dt className="text-gray-500">会社説明</dt>
                    <dd className="text-gray-800 mt-1 whitespace-pre-line">{dashboard.profile.description || '未設定'}</dd>
                  </div>
                  <div>
                    <dt className="text-gray-500">承認状態</dt>
                    <dd className="mt-1">
                      <span className={`text-xs px-2 py-1 rounded-full ${dashboard.profile.is_approved ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                        {dashboard.profile.is_approved ? '承認済み' : '審査中'}
                      </span>
                    </dd>
                  </div>
                </dl>
              ) : (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">会社名</label>
                    <input
                      type="text"
                      value={editForm.company_name}
                      onChange={(e) => setEditForm({ ...editForm, company_name: e.target.value })}
                      className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Webサイト</label>
                    <input
                      type="url"
                      value={editForm.website_url}
                      onChange={(e) => setEditForm({ ...editForm, website_url: e.target.value })}
                      placeholder="https://example.com"
                      className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">会社説明</label>
                    <textarea
                      value={editForm.description}
                      onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                      rows={5}
                      className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 outline-none"
                      placeholder="会社の特徴、サービス内容などを記載してください"
                    />
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  )
}
