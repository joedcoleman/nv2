import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals, fetch, cookies }) => {
  const authToken = cookies.get('auth_token');

  if (locals.user) {
    const [conversationsResponse, settingsResponse] = await Promise.all([
      fetch(`${import.meta.env.VITE_API_BASE_URL}/conversations`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      }),
      fetch(`${import.meta.env.VITE_API_BASE_URL}/settings`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      }),
    ]);
  
    const conversations = await conversationsResponse.json();
    const settings = await settingsResponse.json();
    
    return {
      conversations,
      settings,
    };
  }
  else {
    return {
      conversations: [],
      settings: {}
    }
  }
};