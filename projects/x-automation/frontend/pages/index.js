// AirCle X Automation Website
// Next.js frontend for post management

import { useState, useEffect } from 'react'
import Head from 'next/head'
import { Copy, Twitter, RefreshCw, Check, Loader } from 'lucide-react'

export default function Home() {
  const [posts, setPosts] = useState([])
  const [trendingPosts, setTrendingPosts] = useState([])
  const [activeTab, setActiveTab] = useState('generated')
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(null)
  const [posting, setPosting] = useState(null)

  useEffect(() => {
    fetchPosts()
  }, [])

  const fetchPosts = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/posts')
      const data = await res.json()
      setPosts(data.generated || [])
      setTrendingPosts(data.trending || [])
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  const copyToClipboard = async (text, id) => {
    await navigator.clipboard.writeText(text)
    setCopied(id)
    setTimeout(() => setCopied(null), 2000)
  }

  const postToX = async (post) => {
    setPosting(post.id)
    try {
      const res = await fetch('/api/post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: post.text })
      })
      const result = await res.json()
      if (result.success) {
        alert('投稿完了！')
      } else {
        alert('投稿失败: ' + result.error)
      }
    } catch (e) {
      alert('エラー: ' + e.message)
    }
    setPosting(null)
  }

  const currentPosts = activeTab === 'generated' ? posts : trendingPosts

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Head>
        <title>AirCle X Automation</title>
      </Head>

      <div className="max-w-4xl mx-auto p-6">
        <header className="mb-8">
          <h1 className="text-3xl font-bold mb-2">🦞 AirCle X Automation</h1>
          <p className="text-gray-400">每日自动生成・トレンド監視・自动投稿</p>
        </header>

        {/* Tab Navigation */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setActiveTab('generated')}
            className={`px-4 py-2 rounded-lg ${
              activeTab === 'generated' 
                ? 'bg-blue-600' 
                : 'bg-gray-800 hover:bg-gray-700'
            }`}
          >
            自動生成投稿 ({posts.length})
          </button>
          <button
            onClick={() => setActiveTab('trending')}
            className={`px-4 py-2 rounded-lg ${
              activeTab === 'trending' 
                ? 'bg-orange-600' 
                : 'bg-gray-800 hover:bg-gray-700'
            }`}
          >
            トレンド監視 ({trendingPosts.length})
          </button>
        </div>

        {/* Refresh Button */}
        <div className="mb-6">
          <button
            onClick={fetchPosts}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 rounded-lg hover:bg-gray-700"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            更新
          </button>
        </div>

        {/* Posts List */}
        <div className="space-y-4">
          {currentPosts.map((post) => (
            <div
              key={post.id}
              className="bg-gray-800 rounded-xl p-5 border border-gray-700"
            >
              {/* Pattern Badge */}
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xs px-2 py-1 rounded bg-blue-900 text-blue-200">
                  {post.pattern || 'トレンド'}
                </span>
                {post.topic && (
                  <span className="text-xs px-2 py-1 rounded bg-purple-900 text-purple-200">
                    {post.topic}
                  </span>
                )}
                {post.likes && (
                  <span className="text-xs px-2 py-1 rounded bg-green-900 text-green-200">
                    ❤️ {post.likes}
                  </span>
                )}
              </div>

              {/* Post Text */}
              <div className="whitespace-pre-wrap text-sm mb-4 leading-relaxed">
                {post.text}
              </div>

              {/* Media Preview */}
              {post.media && post.media.length > 0 && (
                <div className="mb-4 flex gap-2 overflow-x-auto">
                  {post.media.map((m, i) => (
                    m.type === 'video' ? (
                      <video
                        key={i}
                        src={m.url}
                        className="h-32 rounded-lg"
                        controls
                      />
                    ) : (
                      <img
                        key={i}
                        src={m.url}
                        alt="Media"
                        className="h-32 rounded-lg object-cover"
                      />
                    )
                  ))}
                </div>
              )}

              {/* Source Link */}
              {post.source_url && (
                <a
                  href={post.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 text-sm hover:underline mb-4 block"
                >
                  📎 参考: {post.source_url}
                </a>
              )}

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={() => copyToClipboard(post.text, post.id)}
                  className="flex items-center gap-2 px-3 py-2 bg-gray-700 rounded-lg hover:bg-gray-600 text-sm"
                >
                  {copied === post.id ? (
                    <>
                      <Check className="w-4 h-4 text-green-400" />
                      コピー済み
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      コピー
                    </>
                  )}
                </button>
                
                <button
                  onClick={() => postToX(post)}
                  disabled={posting === post.id}
                  className="flex items-center gap-2 px-3 py-2 bg-sky-600 rounded-lg hover:bg-sky-500 text-sm"
                >
                  {posting === post.id ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      投稿中...
                    </>
                  ) : (
                    <>
                      <Twitter className="w-4 h-4" />
                      Xに投稿
                    </>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>

        {currentPosts.length === 0 && !loading && (
          <div className="text-center py-12 text-gray-500">
            投稿がありません
          </div>
        )}
      </div>
    </div>
  )
}
