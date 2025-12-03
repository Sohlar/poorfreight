'use client';

import { NewsArticle } from '@/lib/types';
import { formatDateTime, highlightText, isHighlightMatch } from '@/lib/utils';

interface NewsListProps {
  articles: NewsArticle[];
  searchQuery?: string;
  isLoading?: boolean;
}

function HighlightedText({ text, query }: { text: string; query: string }) {
  if (!query) return <>{text}</>;

  const parts = highlightText(text, query);
  return (
    <>
      {parts.map((part, i) => (
        isHighlightMatch(part, query) ? (
          <mark key={i} className="bg-yellow-400 text-gray-900">
            {part}
          </mark>
        ) : (
          <span key={i}>{part}</span>
        )
      ))}
    </>
  );
}

export default function NewsList({
  articles,
  searchQuery = '',
  isLoading = false
}: NewsListProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="bg-gray-800 rounded-lg border border-gray-700 p-4 animate-pulse"
          >
            <div className="h-4 bg-gray-700 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-700 rounded w-1/2 mb-3"></div>
            <div className="h-3 bg-gray-700 rounded w-full"></div>
          </div>
        ))}
      </div>
    );
  }

  if (articles.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-8 text-center">
        <p className="text-gray-400">No articles found</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {articles.map((article) => (
        <article
          key={article.id}
          className="bg-gray-800 rounded-lg border border-gray-700 p-4 hover:border-gray-600 transition-colors"
        >
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-3">
              <span className="inline-block px-2 py-1 text-xs font-medium bg-primary-900 text-primary-300 rounded">
                {article.source}
              </span>
              <time className="text-sm text-gray-400">
                {formatDateTime(article.published_at)}
              </time>
            </div>
          </div>
          <h3 className="text-lg font-semibold mb-2">
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-white hover:text-primary-400 transition-colors"
            >
              <HighlightedText text={article.title} query={searchQuery} />
            </a>
          </h3>
          {article.summary && (
            <p className="text-gray-300 text-sm line-clamp-2">
              <HighlightedText text={article.summary} query={searchQuery} />
            </p>
          )}
        </article>
      ))}
    </div>
  );
}
