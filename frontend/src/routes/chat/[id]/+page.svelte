<script lang="ts">
  import { onMount } from "svelte";
  import ChatWindow from "$lib/components/ChatWindow.svelte";
  import { conversations } from "$lib/stores/ConversationStore";
  import type { PageData } from "./$types";

  export let data: PageData;

  onMount(() => {
    if (data.conversation) {
      conversations.initializeOrUpdateConversation(data.conversation);
    } else {
      console.error("Conversation data is null.");
    }
  });
</script>

<ChatWindow />
