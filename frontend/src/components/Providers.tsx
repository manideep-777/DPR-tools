"use client";

import { ThemeProvider } from "next-themes";
import { Toaster } from "@/components/ui/sonner";
import React from "react";

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider 
      attribute="class" 
      defaultTheme="light" 
      enableSystem={false}
      forcedTheme="light"
      storageKey="theme-preference"
    >
      {children}
      <Toaster />
    </ThemeProvider>
  );
}
