'use client';

import { useEffect } from 'react';

export default function TranslateErrorBoundary() {
  useEffect(() => {
    // Override removeChild to prevent Google Translate errors
    const originalRemoveChild = Element.prototype.removeChild;
    (Element.prototype.removeChild as any) = function(child: Node): Node {
      try {
        if (child && child.parentNode === this) {
          return originalRemoveChild.call(this, child) as Node;
        }
        return child;
      } catch (e) {
        // Silently fail
        return child;
      }
    };

    // Suppress specific console errors
    const originalError = console.error;
    console.error = function(...args: any[]) {
      const errorStr = args[0]?.toString() || '';
      if (
        errorStr.includes('removeChild') ||
        errorStr.includes('not a child') ||
        errorStr.includes('NotFoundError') ||
        errorStr.includes('Failed to execute')
      ) {
        return; // Suppress
      }
      originalError.apply(console, args);
    };

    // Cleanup function to remove Google Translate font tags
    const cleanupTranslation = () => {
      try {
        const fonts = document.querySelectorAll('font');
        fonts.forEach((font) => {
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

    // Listen for navigation events
    const handlePopState = () => cleanupTranslation();
    const handleVisibilityChange = () => {
      if (document.hidden) cleanupTranslation();
    };

    window.addEventListener('popstate', handlePopState);
    window.addEventListener('beforeunload', cleanupTranslation);
    window.addEventListener('hashchange', cleanupTranslation);
    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Cleanup on unmount
    return () => {
      window.removeEventListener('popstate', handlePopState);
      window.removeEventListener('beforeunload', cleanupTranslation);
      window.removeEventListener('hashchange', cleanupTranslation);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      
      // Restore original methods
      Element.prototype.removeChild = originalRemoveChild;
      console.error = originalError;
    };
  }, []);

  return null; // This component doesn't render anything
}
