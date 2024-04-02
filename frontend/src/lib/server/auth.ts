import type { RequestEvent} from "@sveltejs/kit";

export const authenticateUser = (event: RequestEvent) => {
    const {cookies} = event
    const userToken = cookies.get("auth_token")

    if (userToken) {
        return true;
    }
    return null;
}