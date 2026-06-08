import Link from "next/link";

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-400 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-white font-bold text-lg mb-4">UPSC Blog</h3>
            <p className="text-sm">
              AI-powered UPSC preparation platform with comprehensive study
              material, daily quizzes, and advanced evaluation tools.
            </p>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">Free Content</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/blog?category=prelims" className="hover:text-white">Prelims</Link></li>
              <li><Link href="/blog?category=mains" className="hover:text-white">Mains</Link></li>
              <li><Link href="/blog?category=current_affairs" className="hover:text-white">Current Affairs</Link></li>
              <li><Link href="/quiz" className="hover:text-white">Daily Quiz</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">Premium</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/premium/evaluate" className="hover:text-white">AI Answer Evaluator</Link></li>
              <li><Link href="/premium/search" className="hover:text-white">Semantic Search</Link></li>
              <li><Link href="/pricing" className="hover:text-white">Pricing</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">GS Papers</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/blog?gs_paper=gs1" className="hover:text-white">GS Paper 1</Link></li>
              <li><Link href="/blog?gs_paper=gs2" className="hover:text-white">GS Paper 2</Link></li>
              <li><Link href="/blog?gs_paper=gs3" className="hover:text-white">GS Paper 3</Link></li>
              <li><Link href="/blog?gs_paper=gs4" className="hover:text-white">GS Paper 4 (Ethics)</Link></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-800 mt-10 pt-8 text-center text-sm">
          <p>&copy; {new Date().getFullYear()} UPSC Blog. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
