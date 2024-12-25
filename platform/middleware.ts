import { withAuth } from "next-auth/middleware"
import { NextResponse } from "next/server"

export default withAuth(
  function middleware(req) {
    if (
      !req.nextauth.token &&
      !req.nextUrl.pathname.startsWith("/login") &&
      !req.nextUrl.pathname.startsWith("/signup")
    ) {
      return NextResponse.redirect(new URL("/login", req.url))
    }
    return NextResponse.next()
  },
  {
    callbacks: {
      authorized: ({ token }) => !!token,
    },
  }
)

export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|favicon.ico|login|signup).*)",
  ],
}
