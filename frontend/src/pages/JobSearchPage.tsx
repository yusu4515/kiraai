import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { jobsService, applicationsService, type Job, type JobSearchResponse } from '../services/jobs'

export default function JobSearchPage() {
  const navigate = useNavigate()
  const [keyword, setKeyword] = useState('')
  const [location, setLocation] = useState('')
  const [salaryMin, setSalaryMin] = useState('')
  const [results, setResults] = useState<JobSearchResponse | null>(null)
  const [selectedJob, setSelectedJob] = useState<Job | null>(null)
  const [isSearching, setIsSearching] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [appliedJobs, setAppliedJobs] = useState<Set<string>>(new Set())

  const handleSearch = async (page = 1) => {
    if (!keyword.trim()) return
    setIsSearching(true)
    setError(null)
    try {
      const data = await jobsService.search({
        keyword: keyword.trim(),
        location: location.trim() || undefined,
        salary_min: salaryMin ? parseInt(salaryMin) : undefined,
        page,
      })
      setResults(data)
      if (data.jobs.length > 0 && !selectedJob) {
        setSelectedJob(data.jobs[0])
      }
    } catch {
      setError('検索に失敗しました')
    } finally {
      setIsSearching(false)
    }
  }

  const handleSeedJobs = async () => {
    try {
      const { count } = await jobsService.seed()
      if (count > 0) {
        setError(null)
        handleSearch()
      }
    } catch {
      setError('サンプルデータの投入に失敗しました')
    }
  }

  const handleAddToKanban = async (job: Job) => {
    try {
      await applicationsService.create(job.id, 'interested')
      setAppliedJobs((prev) => new Set(prev).add(job.id))
    } catch {
      setError('応募リストへの追加に失敗しました')
    }
  }

  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return '非公開'
    const fmt = (n: number) => `${Math.round(n / 10000)}万円`
    if (min && max) return `${fmt(min)}〜${fmt(max)}`
    if (min) return `${fmt(min)}〜`
    return `〜${fmt(max!)}`
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/dashboard')} className="text-gray-500 hover:text-gray-700">
              ← 戻る
            </button>
            <h1 className="text-lg font-bold text-gray-800">求人検索</h1>
          </div>
          <button
            onClick={() => navigate('/kanban')}
            className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-lg transition-colors"
          >
            応募管理ボード →
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {/* Search Form */}
        <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div className="md:col-span-2">
              <input
                type="text"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="キーワード（職種、スキル、会社名...）"
                className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
            </div>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="勤務地"
              className="border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
            <div className="flex gap-2">
              <select
                value={salaryMin}
                onChange={(e) => setSalaryMin(e.target.value)}
                className="flex-1 border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              >
                <option value="">年収下限</option>
                <option value="3000000">300万円〜</option>
                <option value="4000000">400万円〜</option>
                <option value="5000000">500万円〜</option>
                <option value="6000000">600万円〜</option>
                <option value="8000000">800万円〜</option>
                <option value="10000000">1000万円〜</option>
              </select>
              <button
                onClick={() => handleSearch()}
                disabled={isSearching || !keyword.trim()}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium px-6 py-2 rounded-lg text-sm transition-colors"
              >
                {isSearching ? '...' : '検索'}
              </button>
            </div>
          </div>
          <div className="mt-2 flex gap-2">
            <button
              onClick={handleSeedJobs}
              className="text-xs text-gray-400 hover:text-gray-600 underline"
            >
              サンプル求人を投入
            </button>
          </div>
        </div>

        {/* Results */}
        {results && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Job List */}
            <div className="lg:col-span-1">
              <p className="text-sm text-gray-500 mb-3">
                {results.total}件の求人が見つかりました
              </p>
              <div className="space-y-2">
                {results.jobs.map((job) => (
                  <div
                    key={job.id}
                    onClick={() => setSelectedJob(job)}
                    className={`bg-white rounded-lg border p-3 cursor-pointer transition-colors ${
                      selectedJob?.id === job.id ? 'border-blue-500 ring-1 ring-blue-500' : 'hover:border-gray-300'
                    }`}
                  >
                    <h4 className="font-medium text-sm text-gray-800 line-clamp-1">{job.title}</h4>
                    <p className="text-xs text-gray-500 mt-1">{job.company_name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-gray-400">{job.location}</span>
                      <span className="text-xs text-green-600 font-medium">
                        {formatSalary(job.salary_min, job.salary_max)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
              {results.total > results.per_page && (
                <div className="flex gap-2 mt-4 justify-center">
                  {results.page > 1 && (
                    <button onClick={() => handleSearch(results.page - 1)} className="text-sm text-blue-600 hover:underline">← 前</button>
                  )}
                  <span className="text-sm text-gray-500">{results.page} / {Math.ceil(results.total / results.per_page)}</span>
                  {results.page < Math.ceil(results.total / results.per_page) && (
                    <button onClick={() => handleSearch(results.page + 1)} className="text-sm text-blue-600 hover:underline">次 →</button>
                  )}
                </div>
              )}
            </div>

            {/* Job Detail */}
            <div className="lg:col-span-2">
              {selectedJob ? (
                <div className="bg-white rounded-lg border shadow-sm">
                  <div className="p-6 border-b">
                    <h2 className="text-xl font-bold text-gray-800">{selectedJob.title}</h2>
                    <p className="text-gray-600 mt-1">{selectedJob.company_name}</p>
                    <div className="flex flex-wrap gap-3 mt-3">
                      <span className="text-sm bg-gray-100 text-gray-600 px-2 py-1 rounded">{selectedJob.location}</span>
                      <span className="text-sm bg-green-50 text-green-700 px-2 py-1 rounded font-medium">
                        {formatSalary(selectedJob.salary_min, selectedJob.salary_max)}
                      </span>
                      {selectedJob.job_type && (
                        <span className="text-sm bg-blue-50 text-blue-700 px-2 py-1 rounded">
                          {selectedJob.job_type === 'full_time' ? '正社員' : selectedJob.job_type}
                        </span>
                      )}
                    </div>
                    <div className="flex gap-2 mt-4">
                      <button
                        onClick={() => handleAddToKanban(selectedJob)}
                        disabled={appliedJobs.has(selectedJob.id)}
                        className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
                      >
                        {appliedJobs.has(selectedJob.id) ? '追加済み' : '気になるリストに追加'}
                      </button>
                      {selectedJob.url && (
                        <a
                          href={selectedJob.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium px-4 py-2 rounded-lg transition-colors"
                        >
                          求人元サイトで見る
                        </a>
                      )}
                    </div>
                  </div>
                  <div className="p-6">
                    <h3 className="font-semibold text-gray-800 mb-2">仕事内容</h3>
                    <p className="text-sm text-gray-600 whitespace-pre-line mb-4">{selectedJob.description}</p>
                    {selectedJob.requirements && (
                      <>
                        <h3 className="font-semibold text-gray-800 mb-2">応募条件</h3>
                        <p className="text-sm text-gray-600 whitespace-pre-line">{selectedJob.requirements}</p>
                      </>
                    )}
                  </div>
                </div>
              ) : (
                <div className="bg-white rounded-lg border p-12 text-center text-gray-400">
                  <p>求人を選択してください</p>
                </div>
              )}
            </div>
          </div>
        )}

        {!results && !isSearching && (
          <div className="text-center py-16 text-gray-400">
            <p className="text-4xl mb-4">🔍</p>
            <p>キーワードを入力して求人を検索してください</p>
          </div>
        )}
      </main>
    </div>
  )
}
