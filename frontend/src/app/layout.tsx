import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'ابحث عن الفتوى',
  description: 'نظام بحث ذكي في فتاوى الشيخ ابن باز والشيخ ابن عثيمين',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ar" dir="rtl">
      <body>{children}</body>
    </html>
  )
}
