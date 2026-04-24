import type { Metadata } from "next";
import type { ReactNode } from "react";
import "maplibre-gl/dist/maplibre-gl.css";
import "./globals.css";
import "../styles/editorial.css";

export const metadata: Metadata = {
  title: "Comportamiento del voto panista en Le\u00f3n",
  description: "Pieza editorial interactiva sobre variacion del voto PAN entre 2018 y 2021 por seccion electoral."
};

type RootLayoutProps = {
  children: ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}

