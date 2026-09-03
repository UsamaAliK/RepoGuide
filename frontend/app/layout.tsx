import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RepoGuide",
  description: "Understand any GitHub repository with grounded answers."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
