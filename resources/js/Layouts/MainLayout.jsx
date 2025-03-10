import React from "react"
import "./globals.css"
import { Inter } from "next/font/google"

const inter = Inter({ subsets: ["latin"] })

export const metadata = {
  title: "Formula 1 - The Official Home of Formula 1 Racing",
  description:
    "Enter the world of Formula 1. Your go-to source for the latest F1 news, video highlights, GP results, live timing, in-depth analysis and expert commentary.",
}

export default function MainLayout({ children }) {
    return (
      <html lang="es">
        <body className={inter.className}>{children}</body>
      </html>
    )
  }

