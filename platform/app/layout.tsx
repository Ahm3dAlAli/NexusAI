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
  description: "Your assistant to research scientific literature in minutes instead of hours",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased flex`}
      >
        <ConversationsProvider>
          <Navbar />
          <main className="flex-1">
            {children}
          </main>
        </ConversationsProvider>
      </body>
    </html>
  );
}
