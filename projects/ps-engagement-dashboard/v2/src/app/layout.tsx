import type { Metadata } from "next";
import "./globals.css";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "PS Engagement & Go-Live Dashboard",
  description: "Regional PS engagement coverage, go-live readiness, and delivery risk",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-crystalline-surface">
        {children}
      </body>
    </html>
  );
}
