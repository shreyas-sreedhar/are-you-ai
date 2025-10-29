export const metadata = { title: 'AI Detector' };

import Script from 'next/script';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head />
      <body style={{ fontFamily: 'Inter, ui-sans-serif, system-ui', background: '#0b0e13', color: '#eef2ff', margin: 0 }}>
        <Script
          src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"
          type="module"
          strategy="afterInteractive"
        />
        <header style={{
          position: 'sticky', top: 0, zIndex: 100,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '10px 16px', borderBottom: '1px solid #21302b',
          background: 'linear-gradient(90deg, #0b0e13 0%, #0f1518 100%)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 10, height: 10, background: '#76b900', borderRadius: 2 }} />
            <strong style={{ letterSpacing: 0.6 }}>NVIDIA AI Detector</strong>
            <span style={{ opacity: 0.7, fontSize: 12 }}>powered by NIM</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{
              padding: '4px 8px', borderRadius: 999,
              background: '#10210d', border: '1px solid #21441c', color: '#b7f399',
              fontSize: 11, fontWeight: 700, letterSpacing: 0.4
            }}>NVIDIA Powered</span>
            <div title="Jensen" style={{
              width: 28, height: 28, borderRadius: '50%',
              background: 'linear-gradient(135deg, #1b2a22, #10210d)',
              border: '1px solid #21441c',
              display: 'grid', placeItems: 'center', fontSize: 11,
              color: '#b7f399', fontWeight: 800
            }}>JH</div>
          </div>
        </header>
        <div>
          {children}
        </div>
      </body>
    </html>
  );
}


