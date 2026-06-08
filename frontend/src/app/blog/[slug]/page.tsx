import { Metadata } from "next";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface BlogPostData {
  id: number;
  title: string;
  slug: string;
  author_name: string;
  content: string;
  excerpt: string;
  category: string;
  gs_paper: string;
  micro_topics: string[];
  is_premium: boolean;
  views_count: number;
  published_at: string;
  updated_at: string;
}

async function getPost(slug: string): Promise<BlogPostData | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/blog/posts/${slug}/`, {
      next: { revalidate: 60 },
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function generateMetadata({
  params,
}: {
  params: { slug: string };
}): Promise<Metadata> {
  const post = await getPost(params.slug);
  if (!post) return { title: "Post Not Found" };
  return {
    title: `${post.title} | UPSC Blog`,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      type: "article",
      publishedTime: post.published_at,
    },
  };
}

export default async function BlogPostPage({
  params,
}: {
  params: { slug: string };
}) {
  const post = await getPost(params.slug);

  if (!post) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <h1 className="text-2xl font-bold mb-4">Post Not Found</h1>
        <p className="text-gray-600">The article you&apos;re looking for doesn&apos;t exist.</p>
      </div>
    );
  }

  const CATEGORY_LABELS: Record<string, string> = {
    prelims: "Prelims",
    mains: "Mains",
    current_affairs: "Current Affairs",
    editorial: "Editorial Analysis",
  };

  return (
    <article className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <header className="mb-8">
        <div className="flex items-center gap-3 mb-4">
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
            <span className="text-sm text-gray-500 font-medium">
              {post.gs_paper.toUpperCase()}
            </span>
          )}
          {post.is_premium && <span className="badge-premium">Premium</span>}
        </div>
        <h1 className="text-3xl md:text-4xl font-bold mb-4">{post.title}</h1>
        <div className="flex items-center text-sm text-gray-500 gap-4">
          <span>By {post.author_name}</span>
          <span>{new Date(post.published_at).toLocaleDateString("en-IN", {
            year: "numeric",
            month: "long",
            day: "numeric",
          })}</span>
          <span>{post.views_count} views</span>
        </div>
        {post.micro_topics.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-4">
            {post.micro_topics.map((topic) => (
              <span
                key={topic}
                className="text-xs bg-primary-50 text-primary-700 px-3 py-1 rounded-full"
              >
                {topic}
              </span>
            ))}
          </div>
        )}
      </header>

      <div className="prose prose-lg max-w-none">
        {post.content.split("\n").map((paragraph, i) => (
          <p key={i} className="mb-4 text-gray-800 leading-relaxed">
            {paragraph}
          </p>
        ))}
      </div>
    </article>
  );
}
