'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function RAGTestPage() {
  const [query, setQuery] = useState('');
  const [filePath, setFilePath] = useState('/Users/ichiokanaoto/create-next-app/AI学習スプシ：本当に使えるものだけ (2).xlsx');
  const [indexName, setIndexName] = useState('es_documents');
  const [action, setAction] = useState('search');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    if (!query.trim()) {
      setError('クエリを入力してください');
      return;
    }

    if (action === 'process' && !filePath.trim()) {
      setError('ファイルパスを入力してください');
      return;
    }

    setLoading(true);
    setError('');
    setResult('');

    try {
      const response = await fetch('/api/rag', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, filePath, indexName, action }),
      });

      const data = await response.json();

      if (data.error) {
        setError(data.error);
      } else {
        setResult(data.result);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '不明なエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>RAGシステム テスト</CardTitle>
          <CardDescription>ファイルを処理してベクトル化し、意味ベースの検索を行うRAGエージェントをテストします。</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="action">アクション</Label>
              <select
                id="action"
                value={action}
                onChange={(e) => setAction(e.target.value)}
                className="w-full p-2 border rounded-md"
              >
                <option value="search">検索</option>
                <option value="process">ファイル処理</option>
              </select>
            </div>
            <div>
              <Label htmlFor="indexName">インデックス名</Label>
              <Input
                id="indexName"
                type="text"
                value={indexName}
                onChange={(e) => setIndexName(e.target.value)}
                placeholder="例: es_documents"
              />
            </div>
          </div>

          {action === 'process' && (
            <div>
              <Label htmlFor="filePath">ファイルパス</Label>
              <Input
                id="filePath"
                type="text"
                value={filePath}
                onChange={(e) => setFilePath(e.target.value)}
                placeholder="例: /path/to/file.txt"
              />
            </div>
          )}

          <div>
            <Label htmlFor="query">クエリ</Label>
            <Input
              id="query"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={action === 'search' ? '例: 学生時代に力を入れた経験について' : '例: ファイルを処理してください'}
            />
          </div>

          <Button onClick={handleSubmit} disabled={loading} className="w-full">
            {loading ? '処理中...' : action === 'search' ? '検索' : 'ファイル処理'}
          </Button>

          {error && (
            <div className="p-4 border border-red-200 rounded-md bg-red-50">
              <p className="text-red-600">{error}</p>
            </div>
          )}

          {result && (
            <div className="p-4 border rounded-md bg-gray-50">
              <h3 className="font-semibold mb-2">結果:</h3>
              <div className="whitespace-pre-wrap">{result}</div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}