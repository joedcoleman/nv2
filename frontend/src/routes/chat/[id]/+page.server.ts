import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, cookies, params }) => {
  const authToken = cookies.get('auth_token');
  const conversationId = params.id;

  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/conversations/${conversationId}`, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    })

    if (response.ok) {
      const conversation = (await response.json()) as Conversation;
      return { conversation };
    } else {
      // Handle error if the API request fails
      console.error("Failed to fetch conversation");
      return { conversation: null };
    }
  } catch (error) {
    console.error("Error fetching conversation:", error);
    return { conversation: null };
  }
};