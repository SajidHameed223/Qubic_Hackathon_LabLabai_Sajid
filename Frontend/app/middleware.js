// import { NextResponse } from "next/server";

// export function middleware(req) {
//   const token = req.cookies.get("autopilot_token")?.value;

//   const { pathname } = req.nextUrl;

//   const authPaths = ["/signin", "/signup"];

//   // If user is authenticated and trying to access auth pages → redirect to dashboard
//   if (authPaths.includes(pathname)) {
//     if (token) {
//       return NextResponse.redirect(new URL("/dashboard", req.url));
//     }
//     return NextResponse.next();
//   }

//   // Protect dashboard pages
//   if (pathname.startsWith("/dashboard")) {
//     if (!token) {
//       return NextResponse.redirect(new URL("/signin", req.url));
//     }
//   }

//   return NextResponse.next();
// }

// export const config = {
//   matcher: ["/signin", "/signup", "/dashboard/:path*"],
// };
