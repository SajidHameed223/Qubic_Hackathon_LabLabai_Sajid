import { JetBrains_Mono } from "next/font/google";
import "./globals.css";
import ChatbotWidget from "./chatbot/chatbot_button";

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata = {
  title: "Qubic App",
  description: "Autonomous Treasury Management",
};

export default function RootLayout({
  children,
}) {
  return (
    <html lang="en">
      <body
        className={`${jetbrainsMono.variable} antialiased`}
        style={{ fontFamily: 'var(--font-jetbrains-mono)' }}
      >
       
        {children}
        <ChatbotWidget />
       
          

      </body>
    </html>
  );
}