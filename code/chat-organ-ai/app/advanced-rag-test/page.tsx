'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function AdvancedRAGTestPage() {
  const [query, setQuery] = useState('');
  const [filePath, setFilePath] = useState('/Users/ichiokanaoto/create-next-app/AI学習スプシ：本当に使えるものだけ (2).xlsx');
  const [sheetName, setSheetName] = useState('ガクチカ');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!query.trim() || !filePath.trim()) {
      setError('クエリとファイルパスを入力してください');
      return;
    }

    setLoading(true);
    setError('');
    setResult('');

    try {
      const response = await fetch('/api/advanced-rag', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          filePath: filePath.trim(),
          sheetName: sheetName.trim() || undefined,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'APIリクエストに失敗しました');
      }

      setResult(data.result);
    } catch (error) {
      setError(error instanceof Error ? error.message : '不明なエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <Card>
        <CardHeader>
          <CardTitle>Advanced ES RAG System Test</CardTitle>
          <CardDescription>
            MastraのRAGシステムを使用してESデータを検索します
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="filePath">Excelファイルパス</Label>
            <Input
              id="filePath"
              value={filePath}
              onChange={(e) => setFilePath(e.target.value)}
              placeholder="Excelファイルのパスを入力"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="sheetName">シート名（オプション）</Label>
            <Input
              id="sheetName"
              value={sheetName}
              onChange={(e) => setSheetName(e.target.value)}
              placeholder="シート名を入力（空の場合は最初のシート）"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="query">検索クエリ</Label>
            <Input
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="検索したい内容を入力（例: 学生時代、マルハニチロ、コンサルティング）"
            />
          </div>

          <Button 
            onClick={handleSearch} 
            disabled={loading}
            className="w-full"
          >
            {loading ? '検索中...' : 'RAG検索を実行'}
          </Button>

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800 font-medium">エラー:</p>
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {result && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-md">
              <p className="text-green-800 font-medium mb-2">検索結果:</p>
              <div className="text-green-700 whitespace-pre-wrap">{result}</div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
