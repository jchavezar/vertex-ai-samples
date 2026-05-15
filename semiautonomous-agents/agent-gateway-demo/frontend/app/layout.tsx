import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agent Gateway demo",
  description: "Test every part of the Agent Gateway + Agent Identity + 3LO stack",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en"><body className="min-h-screen">{children}</body></html>
  );
}
