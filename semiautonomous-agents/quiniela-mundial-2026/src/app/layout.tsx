import type { Metadata, Viewport } from "next";
import { Space_Grotesk, Chakra_Petch } from "next/font/google";
import "./globals.css";
import { Nav } from "@/components/Nav";
import { BottomNav } from "@/components/BottomNav";
import { NewsBanner } from "@/components/NewsBanner";
import { ChatBot } from "@/components/ChatBot";
import { PlayerProvider } from "@/lib/player-context";
import { LocaleProvider } from "@/lib/i18n";
import { SwRegister } from "@/components/SwRegister";
import { PushActivationNag } from "@/components/PushActivationFlow";
import { DeferredLayoutChrome } from "@/components/DeferredLayoutChrome";
import { LegacyModeCleanup } from "@/components/LegacyModeCleanup";
import { PageViewTracker } from "@/components/PageViewTracker";
import { ScrollRestoration } from "@/components/ScrollRestoration";

const grotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-grotesk",
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

const chakra = Chakra_Petch({
  subsets: ["latin"],
  variable: "--font-chakra",
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Quiniela Charales 2026 · La Bolsa de $1000",
  description: "Quiniela del Mundial FIFA 2026 entre Charales. 10 compas, $1000 al ganador.",
  applicationName: "Charales 26",
  appleWebApp: { capable: true, title: "Charales 26", statusBarStyle: "black-translucent" },
};

export const viewport: Viewport = {
  themeColor: "#0b0f17",
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es" className={`${grotesk.variable} ${chakra.variable}`}>
      <body className="min-h-screen bg-canvas">
        <div aria-hidden className="q26-watermark" />
        <LocaleProvider>
          <PlayerProvider>
            <LegacyModeCleanup />
            <PageViewTracker />
            <ScrollRestoration />
            <NewsBanner />
            <Nav />
            <main className="pb-32 md:pb-12">{children}</main>
            <BottomNav />
            <ChatBot />
            <SwRegister />
            <PushActivationNag />
            <DeferredLayoutChrome />
          </PlayerProvider>
        </LocaleProvider>
      </body>
    </html>
  );
}
