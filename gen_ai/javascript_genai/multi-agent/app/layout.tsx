import * as React from "react";

export default function (
    {children,}: {children: React.ReactNode}) {
    return (
        <html lang="en">
        <body>{children}</body>
        </html>
    )
}