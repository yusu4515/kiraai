import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { user, isAuthenticated, isLoading, fetchUser, logout } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    fetchUser()
  }, [isAuthenticated, fetchUser, navigate])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  if (isLoading || !user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">KiraAI</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">
              {user.full_name || user.email}
            </span>
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
              {user.role === 'agent' ? 'エージェント' : '求職者'}
            </span>
            <button
              onClick={handleLogout}
              className="text-sm text-gray-500 hover:text-gray-700 underline"
            >
              ログアウト
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800">
            ようこそ、{user.full_name || 'ユーザー'}さん
          </h2>
          <p className="text-gray-600 mt-1">KiraAI ダッシュボード</p>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* AI Hearing */}
          <div className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow">
            <div className="text-3xl mb-4">🤖</div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              AIヒアリング
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              AIとの対話で、あなたの強み・経歴・希望条件を整理します
            </p>
            <button
              onClick={() => navigate('/hearing')}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors"
            >
              ヒアリングを開始
            </button>
          </div>

          {/* Document Generation */}
          <div className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow">
            <div className="text-3xl mb-4">📄</div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              書類自動生成
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              履歴書・職務経歴書をAIが自動生成。PDF/Word出力対応
            </p>
            <button
              onClick={() => navigate('/documents')}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors"
            >
              書類を生成
            </button>
          </div>

          {/* Job Search */}
          <div className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow">
            <div className="text-3xl mb-4">🔍</div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              求人検索
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              複数の転職サイトを横断して、最適な求人を検索します
            </p>
            <button
              onClick={() => navigate('/jobs')}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors"
            >
              求人を検索
            </button>
          </div>

          {/* Kanban Board */}
          <div className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow">
            <div className="text-3xl mb-4">📋</div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              応募管理
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              応募状況をカンバンボードで一覧管理できます
            </p>
            <button
              onClick={() => navigate('/kanban')}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors"
            >
              応募管理を開く
            </button>
          </div>

          {/* Profile */}
          <div className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow">
            <div className="text-3xl mb-4">👤</div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              プロフィール
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              マスタープロフィールを編集・管理します
            </p>
            <button
              className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors opacity-50 cursor-not-allowed"
              disabled
            >
              Coming Soon
            </button>
          </div>

          {/* Agent Dashboard (for agents only) */}
          {user.role === 'agent' && (
            <div className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow border-orange-200">
              <div className="text-3xl mb-4">🏢</div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                エージェント管理
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                掲載情報・レポート・スカウト管理
              </p>
              <button
                onClick={() => navigate('/agent')}
                className="w-full bg-orange-600 hover:bg-orange-700 text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors"
              >
                管理画面を開く
              </button>
            </div>
          )}
        </div>

        {/* User Info Card */}
        <div className="mt-8 bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">アカウント情報</h3>
          <dl className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <dt className="text-gray-500">メールアドレス</dt>
              <dd className="text-gray-800 font-medium">{user.email}</dd>
            </div>
            <div>
              <dt className="text-gray-500">氏名</dt>
              <dd className="text-gray-800 font-medium">{user.full_name || '未設定'}</dd>
            </div>
            <div>
              <dt className="text-gray-500">アカウント種類</dt>
              <dd className="text-gray-800 font-medium">
                {user.role === 'agent' ? '転職エージェント' : '求職者'}
              </dd>
            </div>
            <div>
              <dt className="text-gray-500">登録日</dt>
              <dd className="text-gray-800 font-medium">
                {new Date(user.created_at).toLocaleDateString('ja-JP')}
              </dd>
            </div>
          </dl>
        </div>
      </main>
    </div>
  )
}
