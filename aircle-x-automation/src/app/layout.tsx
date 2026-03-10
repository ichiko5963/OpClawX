import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AirCle X Automation',
  description: 'X投稿自動化システム',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className="bg-dark-900 text-white min-h-screen">
        {children}
      </body>
    </html>
  );
}
