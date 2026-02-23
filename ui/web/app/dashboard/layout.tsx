/*
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0

You may:
Study
Modify
Use for internal security testing

You may NOT:
Offer as a commercial service
Sell derived competing products
*/

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { isSessionTokenValid } from "../lib/auth-store";

export default async function DashboardLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const cookieStore = await cookies();
  const sessionToken = cookieStore.get("spectrastrike_session")?.value;

  if (!sessionToken || !isSessionTokenValid(sessionToken)) {
    redirect("/login");
  }

  return children;
}

