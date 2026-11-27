
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ZealWithin | Keep the Researcher in You Alive",
  description:
    "Discover, organize, and stay updated with research that matters to you.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">
        {children}
      </body>
    </html>
  );
}
