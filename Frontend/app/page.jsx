"use client";
import React from "react";
import { redirect } from "next/navigation";
// import Dashborad from "./dashborad/page";
// import Dashboard from "./dashboard/page";

function page() {
  redirect("/dashboard");
  return null;
}

export default page;
