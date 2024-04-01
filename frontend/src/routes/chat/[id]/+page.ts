// +page.server.ts

import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
  const conversationId = params.id;

  try {
    // Fetch the conversation from the API using the provided fetch function
    const response = await fetch(`http://localhost:8000/conversations/${conversationId}`);

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