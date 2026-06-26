import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/** Always land on the welcome page when visiting the site root. */
export function middleware(request: NextRequest) {
  if (request.nextUrl.pathname === "/") {
    return NextResponse.redirect(new URL("/welcome", request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/"],
};
