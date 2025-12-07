"use client";
import AuthForm from "@/components/forms/AuthForm";
import OAuthButtons from "@/components/forms/OAuthButtons";
import { useRouter } from "next/navigation";

export default function SignInPage() {
  const router = useRouter();

  const handleEmailSignIn = async (data) => {
    try {
      const res = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: data.email,
          password: data.password,
        }),
      });

      if (!res.ok) throw new Error("Login failed");

      const loginData = await res.json();
      document.cookie = `autopilot_token=${loginData.access_token}; path=/;`;

      router.push("/dashboard");
    } catch (err) {
      console.error(err);
      alert("Login failed");
    }
  };

  //   const handleGoogle = () => {
  //     console.log("Sign In with Google");
  //     // Redirect to Google OAuth
  //   };

  //   const handleQubic = () => {
  //     console.log("Sign In with Qubic Wallet");
  //     // Trigger Qubic wallet login
  //   };

  return (
    <div className="min-h-screen bg-[#101010] flex flex-col items-center py-12">
      <AuthForm mode="signin" onSubmit={handleEmailSignIn} />
      {/* <OAuthButtons onGoogle={handleGoogle} onQubic={handleQubic} /> */}
    </div>
  );
}
