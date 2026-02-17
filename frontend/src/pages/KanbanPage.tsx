import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { applicationsService, jobsService, type ApplicationData, type Job } from '../services/jobs'

const STATUSES = [
  { key: 'interested', label: '気になる', color: 'bg-gray-100 border-gray-300' },
  { key: 'applied', label: '応募済み', color: 'bg-blue-50 border-blue-300' },
  { key: 'interviewing', label: '面接中', color: 'bg-yellow-50 border-yellow-300' },
  { key: 'offered', label: '内定', color: 'bg-green-50 border-green-300' },
  { key: 'rejected', label: '見送り', color: 'bg-red-50 border-red-300' },
]

interface AppWithJob extends ApplicationData {
  job?: Job
}

export default function KanbanPage() {
  const navigate = useNavigate()
  const [applications, setApplications] = useState<AppWithJob[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadApplications()
  }, [])

  const loadApplications = async () => {
    try {
      const apps = await applicationsService.list()
      // Load job details for each application
      const appsWithJobs: AppWithJob[] = await Promise.all(
        apps.map(async (app) => {
          if (app.job_id) {
            try {
              const job = await jobsService.get(app.job_id)
              return { ...app, job }
            } catch {
              return app
            }
          }
          return app
        })
      )
      setApplications(appsWithJobs)
    } catch {
      setError('応募データの読み込みに失敗しました')
    } finally {
      setIsLoading(false)
    }
  }

  const handleStatusChange = async (appId: string, newStatus: string) => {
    try {
      await applicationsService.update(appId, { status: newStatus })
      setApplications((prev) =>
        prev.map((a) => (a.id === appId ? { ...a, status: newStatus } : a))
      )
    } catch {
      setError('ステータスの更新に失敗しました')
    }
  }

  const handleDelete = async (appId: string) => {
    if (!window.confirm('この応募を削除しますか？')) return
    try {
      await applicationsService.delete(appId)
      setApplications((prev) => prev.filter((a) => a.id !== appId))
      setError(null)
    } catch {
      setError('削除に失敗しました')
    }
  }

  const getAppsForStatus = (status: string) =>
    applications.filter((a) => a.status === status)

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/dashboard')} className="text-gray-500 hover:text-gray-700">
              ← 戻る
            </button>
            <h1 className="text-lg font-bold text-gray-800">応募管理</h1>
          </div>
          <button
            onClick={() => navigate('/jobs')}
            className="text-sm bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg transition-colors"
          >
            求人検索 →
          </button>
        </div>
      </header>

      <main className="max-w-full mx-auto px-4 py-6">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {applications.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <p className="text-4xl mb-4">📋</p>
            <p className="mb-4">まだ応募管理に求人がありません</p>
            <button
              onClick={() => navigate('/jobs')}
              className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
            >
              求人を検索する
            </button>
          </div>
        ) : (
          <div className="flex gap-4 overflow-x-auto pb-4">
            {STATUSES.map((col) => (
              <div key={col.key} className="flex-shrink-0 w-72">
                <div className={`rounded-lg border-2 ${col.color} p-3`}>
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-sm text-gray-700">{col.label}</h3>
                    <span className="text-xs bg-white text-gray-500 px-2 py-0.5 rounded-full">
                      {getAppsForStatus(col.key).length}
                    </span>
                  </div>
                  <div className="space-y-2 min-h-[100px]">
                    {getAppsForStatus(col.key).map((app) => (
                      <div
                        key={app.id}
                        className="bg-white rounded-lg border p-3 shadow-sm"
                      >
                        <h4 className="font-medium text-sm text-gray-800 line-clamp-1">
                          {app.job?.title || '不明な求人'}
                        </h4>
                        <p className="text-xs text-gray-500 mt-1">
                          {app.job?.company_name || ''}
                        </p>
                        {(app.job?.salary_min || app.job?.salary_max) && (
                          <p className="text-xs text-green-600 mt-1">
                            {app.job?.salary_min && app.job?.salary_max
                              ? `${Math.round(app.job.salary_min / 10000)}〜${Math.round(app.job.salary_max / 10000)}万円`
                              : app.job?.salary_min
                                ? `${Math.round(app.job.salary_min / 10000)}万円〜`
                                : `〜${Math.round(app.job!.salary_max! / 10000)}万円`}
                          </p>
                        )}
                        <div className="flex gap-1 mt-2 flex-wrap">
                          {STATUSES.filter((s) => s.key !== app.status).map((s) => (
                            <button
                              key={s.key}
                              onClick={() => handleStatusChange(app.id, s.key)}
                              className="text-[10px] text-gray-500 hover:text-blue-600 hover:bg-blue-50 px-1.5 py-0.5 rounded border transition-colors"
                            >
                              → {s.label}
                            </button>
                          ))}
                          <button
                            onClick={() => handleDelete(app.id)}
                            className="text-[10px] text-red-400 hover:text-red-600 hover:bg-red-50 px-1.5 py-0.5 rounded border transition-colors ml-auto"
                          >
                            削除
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
