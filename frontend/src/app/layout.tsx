import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Support Worker",
  description: "Customer support assistant for common questions.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
