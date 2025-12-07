"use client";

import { useRouter } from "next/navigation";
import AuthForm from "@/components/forms/AuthForm";
import OAuthButtons from "@/components/forms/OAuthButtons";

export default function SignUpPage() {
  const router = useRouter();

  const handleEmailSignUp = async (data) => {
    try {
      // Register user
      const res = await fetch("http://localhost:8000/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: data.email,
          password: data.password,
          full_name: data.fullName,
        }),
      });

      if (!res.ok) throw new Error("Signup failed");

      // Immediately login to get token
      const loginRes = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: data.email,
          password: data.password,
        }),
      });

      const loginData = await loginRes.json();
      document.cookie = `autopilot_token=${loginData.access_token}; path=/;`;

      router.push("/dashboard");
    } catch (err) {
      console.error(err);
      alert("Signup failed");
    }
  };

  // const handleGoogle = () => {
  //   console.log("Sign Up with Google");
  // };

  // const handleQubic = () => {
  //   console.log("Sign Up with Qubic Wallet");
  // };

  return (
    <div className="min-h-screen bg-[#101010] flex flex-col justify-center">
      <AuthForm mode="signup" onSubmit={handleEmailSignUp} />
      {/* <OAuthButtons onGoogle={handleGoogle} onQubic={handleQubic} /> */}
    </div>
  );
}
