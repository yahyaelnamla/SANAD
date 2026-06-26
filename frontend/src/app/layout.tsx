import { Inter, Noto_Sans_Arabic, Tajawal } from "next/font/google";

import { Providers } from "@/components/Providers";
import { SETTINGS_STORAGE_KEY } from "@/lib/constants";

import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-geist-sans" });
const tajawal = Tajawal({
  subsets: ["arabic"],
  weight: ["400", "500", "700"],
  variable: "--font-tajawal",
});
const notoArabic = Noto_Sans_Arabic({
  subsets: ["arabic"],
  variable: "--font-noto-arabic",
});

const localeBootstrapScript = `(function(){try{var raw=localStorage.getItem(${JSON.stringify(SETTINGS_STORAGE_KEY)});if(!raw)return;var parsed=JSON.parse(raw);var locale=(parsed&&parsed.state&&parsed.state.locale)||"ar";document.documentElement.lang=locale;document.documentElement.dir=locale==="ar"?"rtl":"ltr";}catch(e){}})();`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ar" dir="rtl" className="h-full" suppressHydrationWarning>
      <head>
        <title>SANAD — Shariah Financial Reasoning</title>
        <meta name="description" content="Evidence-based Shariah financial reasoning platform" />
        <meta name="theme-color" content="#08111F" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <link rel="manifest" href="/manifest.webmanifest" />
        <link rel="apple-touch-icon" href="/icons/icon-192.svg" />
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
        <script dangerouslySetInnerHTML={{ __html: localeBootstrapScript }} />
      </head>
      <body
        className={`${inter.variable} ${tajawal.variable} ${notoArabic.variable} font-arabic h-full min-h-0 antialiased`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
