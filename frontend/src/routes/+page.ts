import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
  const [conversationsResponse, settingsResponse] = await Promise.all([
    fetch("http://localhost:8000/conversations"),
    fetch("http://localhost:8000/settings")
  ]);

  const conversations = await conversationsResponse.json();
  const settings = await settingsResponse.json();

  return {
    conversations,
    settings,
  };
};
