import type { Metadata } from "next";

import { Footer, Nav } from "../components/Chrome";
import "./globals.css";

export const metadata: Metadata = {
  title: "RUAI — are you AI?",
  description:
    "RUAI checks whether a video was made by AI, whether a message is a scam, and whether a story holds up — and explains the answer in plain words. Built for older adults.",
  icons: { icon: "/favicon.svg" },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        {/* Runs before paint. Scroll reveals only hide their content once
            this has confirmed scripting works, so a JS failure costs the
            animation rather than the whole page. */}
        <script
          dangerouslySetInnerHTML={{
            __html: `document.documentElement.dataset.js="on"`,
          }}
        />
      </head>
      <body>
        <Nav />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}
