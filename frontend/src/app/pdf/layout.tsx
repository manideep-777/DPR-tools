import Providers from "@/components/Providers";

export default function PDFLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <Providers>
      <main className="min-h-screen bg-background">{children}</main>
    </Providers>
  );
}
