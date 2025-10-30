import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Script from "next/script"; // Import Next.js Script component for optimal loading
import "./globals.css";
import Navbar from "@/components/layout/Navbar";
import Providers from "@/components/Providers";
import TranslateErrorBoundary from "@/components/TranslateErrorBoundary";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "MSME DPR Generator",
  description: "AI-powered Detailed Project Report Generator for MSMEs",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* Initialize Google Translate callback function before the script loads */}
        <Script
          id="google-translate-init"
          strategy="beforeInteractive"
          dangerouslySetInnerHTML={{
            __html: `
              function googleTranslateElementInit() {
                new google.translate.TranslateElement(
                  {
                    pageLanguage: 'en', // Default page language is English
                    includedLanguages: 'en,te', // Only English and Telugu available
                    layout: google.translate.TranslateElement.InlineLayout.HORIZONTAL, // Horizontal dropdown layout
                    autoDisplay: false, // Don't auto-display translation banner
                  },
                  'google_translate_element' // ID of the div where dropdown will appear
                );
              }
              
              // Comprehensive fix for Google Translate + React navigation conflicts
              if (typeof window !== 'undefined') {
                // Suppress all Google Translate related errors
                const originalError = console.error;
                console.error = function(...args) {
                  const errorStr = args[0]?.toString() || '';
                  if (
                    errorStr.includes('removeChild') || 
                    errorStr.includes('not a child') ||
                    errorStr.includes('NotFoundError') ||
                    errorStr.includes('Node.removeChild') ||
                    errorStr.includes('Failed to execute')
                  ) {
                    return; // Suppress these errors
                  }
                  originalError.apply(console, args);
                };
                
                // Override DOM removeChild to prevent errors
                const originalRemoveChild = Element.prototype.removeChild;
                Element.prototype.removeChild = function(child) {
                  try {
                    // Check if child is actually a child of this element
                    if (child && child.parentNode === this) {
                      return originalRemoveChild.call(this, child);
                    }
                    return child;
                  } catch (e) {
                    // Silently fail instead of throwing error
                    return child;
                  }
                };
                
                window.addEventListener('load', function() {
                  // Monitor for translation changes
                  const observer = new MutationObserver(function(mutations) {
                    const html = document.documentElement;
                    if (html.classList.contains('translated-ltr') || html.classList.contains('translated-rtl')) {
                      document.body.classList.add('translated');
                    } else {
                      document.body.classList.remove('translated');
                    }
                  });
                  
                  observer.observe(document.documentElement, {
                    attributes: true,
                    attributeFilter: ['class']
                  });
                  
                  // Listen for Next.js navigation events
                  const cleanupTranslation = function() {
                    try {
                      const fonts = document.querySelectorAll('font');
                      fonts.forEach(font => {
                        try {
                          if (font.parentNode) {
                            const text = document.createTextNode(font.textContent || '');
                            font.parentNode.replaceChild(text, font);
                          }
                        } catch (e) {
                          // Ignore individual errors
                        }
                      });
                    } catch (e) {
                      // Ignore cleanup errors
                    }
                  };
                  
                  // Multiple cleanup triggers for different navigation scenarios
                  document.addEventListener('visibilitychange', function() {
                    if (document.hidden) {
                      cleanupTranslation();
                    }
                  });
                  
                  // Cleanup before unload
                  window.addEventListener('beforeunload', cleanupTranslation);
                  
                  // Cleanup on popstate (back/forward button)
                  window.addEventListener('popstate', cleanupTranslation);
                  
                  // Cleanup on hashchange
                  window.addEventListener('hashchange', cleanupTranslation);
                });
              }
            `,
          }}
        />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        suppressHydrationWarning
      >
        {/* Load Google Translate script after page is interactive */}
        <Script
          src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"
          strategy="afterInteractive"
        />

        {/* Google Translate dropdown container - fixed at bottom-right corner */}
        {/* This dropdown itself should not be translated */}
        <div
          id="google_translate_element"
          className="notranslate fixed bottom-4 right-4 z-9999"
          style={{
            backgroundColor: 'white',
            padding: '8px 12px',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          }}
        ></div>

        <Providers>
          <TranslateErrorBoundary />
          <Navbar />
          <main className="min-h-screen bg-background">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
