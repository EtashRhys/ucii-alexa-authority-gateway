import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "UCII for Alexa+",
  description: "Universal Cryptographic Identity Infrastructure. A personal authority layer for Alexa+.",
  other: {
    "codex-preview": "development",
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
