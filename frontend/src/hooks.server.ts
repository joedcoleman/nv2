import { authenticateUser } from "$lib/server/auth";
import { redirect, type Handle } from "@sveltejs/kit";

declare global {
  namespace App {
    interface Locals {
      user: boolean | null;
    }
  }
}

export const handle: Handle = async ({event, resolve}) => {
    event.locals.user = authenticateUser(event)
    if (!event.url.pathname.startsWith('/login')) {
        if (!event.locals.user) {
            throw redirect(303, '/login');
        }
    }
    const response = await resolve(event)

    return response
}