import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { ConversationsProvider } from '@/context/ConversationsContext'
import Navbar from '@/components/navbar'

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "NexusAI",
  description: "Research scientific literature in minutes, not hours",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased flex no-scrollbar overflow-y-hidden`}
      >
        <ConversationsProvider>
          <Navbar />
          <main className="flex-1 no-scrollbar overflow-y-auto">
            {children}
          </main>
        </ConversationsProvider>
      </body>
    </html>
  );
}
