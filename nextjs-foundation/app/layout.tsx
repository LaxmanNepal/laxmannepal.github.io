import type { Metadata } from "next";
import "./globals.css";
import SharedShell from "@/components/shared-shell";

export const metadata: Metadata = {
  metadataBase: new URL("https://laxmannepal.com.np"),
  title: { default: "Laxman Nepal — Technology, Tools & AI", template: "%s | Laxman Nepal" },
  description: "Practical technology news, reviews, guides, product research, free tools, AI resources and YouTube intelligence.",
  openGraph: { title: "Laxman Nepal — Technology, Tools & AI", description: "Technology, product research, free tools, AI and creator intelligence.", url: "https://laxmannepal.com.np", siteName: "Laxman Nepal", type: "website" },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><head><link rel="stylesheet" href="/assets/css/shared-shell.css" /></head><body><SharedShell>{children}</SharedShell></body></html>;
}
