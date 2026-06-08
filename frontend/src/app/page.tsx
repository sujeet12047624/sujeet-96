import Link from "next/link";

const features = [
  {
    title: "Prelims Practice",
    description: "Daily MCQ quizzes from current affairs with AI-generated explanations.",
    href: "/quiz",
    badge: "Free",
    color: "green",
  },
  {
    title: "Mains Answer Writing",
    description: "GS Paper articles, answer strategies, and editorial analysis.",
    href: "/blog?category=mains",
    badge: "Free",
    color: "blue",
  },
  {
    title: "AI Answer Evaluator",
    description: "Get your Mains answers evaluated by Claude AI with detailed rubric feedback.",
    href: "/premium/evaluate",
    badge: "Premium",
    color: "yellow",
  },
  {
    title: "Semantic Search",
    description: "RAG-powered search across UPSC corpus, NCERTs, and official syllabi.",
    href: "/premium/search",
    badge: "Premium",
    color: "yellow",
  },
];

export default function HomePage() {
  return (
    <div>
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-700 via-primary-800 to-primary-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Master UPSC with{" "}
              <span className="text-accent-400">AI-Powered</span> Preparation
            </h1>
            <p className="text-xl md:text-2xl text-primary-200 mb-10 max-w-3xl mx-auto">
              Comprehensive blog platform with daily quizzes, AI answer evaluation,
              and semantic search across the entire UPSC syllabus.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/blog"
                className="btn-primary text-lg px-8 py-3 inline-block text-center"
              >
                Explore Articles
              </Link>
              <Link
                href="/pricing"
                className="btn-secondary text-lg px-8 py-3 inline-block text-center !text-white !border-white/30 hover:!bg-white/10"
              >
                View Premium Plans
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-3xl font-bold text-center mb-12">
          Everything You Need for UPSC Success
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature) => (
            <Link key={feature.title} href={feature.href}>
              <div className="card hover:shadow-md transition-shadow h-full">
                <span
                  className={`inline-block px-3 py-1 rounded-full text-xs font-semibold mb-3 ${
                    feature.color === "green"
                      ? "bg-green-100 text-green-800"
                      : feature.color === "blue"
                      ? "bg-blue-100 text-blue-800"
                      : "bg-accent-100 text-accent-800"
                  }`}
                >
                  {feature.badge}
                </span>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-600 text-sm">{feature.description}</p>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Stats */}
      <section className="bg-gray-100 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { value: "500+", label: "Articles" },
              { value: "4", label: "GS Papers" },
              { value: "Daily", label: "MCQ Quizzes" },
              { value: "AI", label: "Powered Evaluation" },
            ].map((stat) => (
              <div key={stat.label}>
                <div className="text-3xl font-bold text-primary-700">{stat.value}</div>
                <div className="text-gray-600 mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
