/*
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0

You may:
Study
Modify
Use for internal security testing

You may NOT:
Offer as a commercial service
Sell derived competing products
*/

import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Space_Grotesk } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-display",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "SpectraStrike UI",
  description: "Dockerized operator web foundation for SpectraStrike"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  const copyrightYear = new Date().getFullYear();

  return (
    <html lang="en">
      <body className={`${inter.variable} ${spaceGrotesk.variable} ${jetbrainsMono.variable}`}>
        <div className="flex min-h-screen flex-col">
          <div className="flex-1">{children}</div>
          <footer className="mx-auto w-full max-w-6xl px-6 pb-6">
            <div className="spectra-panel mt-6 flex flex-col gap-2 border-borderSubtle/80 bg-surfaceElevated/70 px-4 py-3 text-xs text-slate-300 sm:flex-row sm:items-center sm:justify-between">
              <p>Copyright (c) {copyrightYear} NyxeraLabs. All rights reserved.</p>
              <p>
                Licensed under BSL 1.1. Change Date: 2033-02-22 -&gt; Apache-2.0.
              </p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
