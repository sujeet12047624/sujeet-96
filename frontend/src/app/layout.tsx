import type { Metadata } from "next";
import { Toaster } from "react-hot-toast";

import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "UPSC Blog - Your Complete IAS Preparation Platform",
  description:
    "Comprehensive UPSC preparation with AI-powered answer evaluation, daily MCQ quizzes, and curated study material for Prelims & Mains.",
  keywords: "UPSC, IAS, Civil Services, Prelims, Mains, Current Affairs, GS Paper",
  openGraph: {
    title: "UPSC Blog - AI-Powered IAS Preparation",
    description: "Comprehensive UPSC preparation platform with AI features",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow">{children}</main>
        <Footer />
        <Toaster position="top-right" />
      </body>
    </html>
  );
}
