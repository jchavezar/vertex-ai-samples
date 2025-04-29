import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
    title: 'Sustainability Assistant',
    description: 'Deloitte Sustainability Assistant',
};

export default function RootLayout({
                                       children,
                                   }: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
        <body>{children}</body>
        </html>
    );
}