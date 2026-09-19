import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://laxmannepal.com.np"),
  title: {
    default: "Laxman Nepal",
    template: "%s | Laxman Nepal",
  },
  description: "Technology, AI, tutorials, tools and creator resources from Laxman Nepal.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
