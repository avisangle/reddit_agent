import type { Metadata } from "next";
import { Plus_Jakarta_Sans, IBM_Plex_Mono, Lora } from "next/font/google";
import "./globals.css";
import { SiteNavbar } from "@/components/site-navbar";

const plusJakartaSans = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["200", "300", "400", "500", "600", "700", "800"],
  variable: "--font-sans",
});

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["100", "200", "300", "400", "500", "600", "700"],
  variable: "--font-mono",
});

const lora = Lora({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-serif",
});

export const metadata: Metadata = {
  title: "Reddit Agent Documentation",
  description: "Documentation for the Reddit Comment Engagement Agent - A compliance-first, AI-powered Reddit engagement bot",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${plusJakartaSans.variable} ${ibmPlexMono.variable} ${lora.variable} min-h-screen bg-background font-sans antialiased`}>
        <SiteNavbar />
        <main className="container mx-auto px-4 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
