"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { blogService } from "@/services/blog";
import type { BlogPost } from "@/types";

const CATEGORY_LABELS: Record<string, string> = {
  prelims: "Prelims",
  mains: "Mains",
  current_affairs: "Current Affairs",
  editorial: "Editorial Analysis",
};

function BlogListContent() {
  const searchParams = useSearchParams();
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [loading, setLoading] = useState(true);
  const category = searchParams.get("category") || "";
  const gsPaper = searchParams.get("gs_paper") || "";
  const search = searchParams.get("search") || "";

  useEffect(() => {
    setLoading(true);
    blogService
      .getPosts({ category, gs_paper: gsPaper, search })
      .then((data) => setPosts(data.results))
      .catch(() => setPosts([]))
      .finally(() => setLoading(false));
  }, [category, gsPaper, search]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
        <h1 className="text-3xl font-bold">
          {category ? CATEGORY_LABELS[category] || "Articles" : "All Articles"}
        </h1>
        <div className="flex gap-2 mt-4 md:mt-0 flex-wrap">
          {Object.entries(CATEGORY_LABELS).map(([value, label]) => (
            <Link
              key={value}
              href={`/blog?category=${value}`}
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
                category === value
                  ? "bg-primary-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              {label}
            </Link>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/4 mb-3"></div>
              <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-full mb-1"></div>
              <div className="h-4 bg-gray-200 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      ) : posts.length === 0 ? (
        <p className="text-gray-500 text-center py-12">No articles found.</p>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {posts.map((post) => (
            <Link key={post.id} href={`/blog/${post.slug}`}>
              <article className="card hover:shadow-md transition-shadow h-full flex flex-col">
                <div className="flex items-center gap-2 mb-3">
                  <span
                    className={
                      post.category === "prelims"
                        ? "badge-prelims"
                        : post.category === "mains"
                        ? "badge-mains"
                        : "bg-gray-100 text-gray-700 text-xs font-medium px-2.5 py-0.5 rounded-full"
                    }
                  >
                    {CATEGORY_LABELS[post.category] || post.category}
                  </span>
                  {post.gs_paper && (
                    <span className="text-xs text-gray-500">
                      {post.gs_paper.toUpperCase()}
                    </span>
                  )}
                  {post.is_premium && <span className="badge-premium">Premium</span>}
                </div>
                <h2 className="text-lg font-semibold mb-2 line-clamp-2">{post.title}</h2>
                <p className="text-gray-600 text-sm line-clamp-3 flex-grow">
                  {post.excerpt}
                </p>
                <div className="flex items-center justify-between mt-4 text-xs text-gray-500">
                  <span>{post.author_name}</span>
                  <span>{new Date(post.published_at).toLocaleDateString("en-IN")}</span>
                </div>
                {post.micro_topics.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {post.micro_topics.slice(0, 3).map((topic) => (
                      <span
                        key={topic}
                        className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded"
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                )}
              </article>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default function BlogListPage() {
  return (
    <Suspense fallback={<div className="max-w-7xl mx-auto px-4 py-12 text-center">Loading...</div>}>
      <BlogListContent />
    </Suspense>
  );
}
