<script lang="ts">
  import { onMount } from "svelte";
  import { fade, fly } from "svelte/transition";
  import { webSocketStore, isConnected } from "$lib/stores/WebSocketStore";
  import { currentConversation } from "$lib/stores/ConversationStore";
  import ChatInput from "$lib/components/ChatInput.svelte";
  import Conversations from "$lib/components/Conversations.svelte";
  import ChatWindow from "$lib/components/ChatWindow.svelte";
  import ModelSelector from "$lib/components/common/ModelSelector.svelte";

  function handleUserMessage(event: CustomEvent<Message>) {
    const message = event.detail;
    webSocketStore.sendMessage(message);
  }

  onMount(() => {
    currentConversation.set(null);
  });
</script>

{#if $currentConversation}
  <ChatWindow />
{:else}
  <div
    class="h-full flex flex-col justify-start items-center max-w-xl mx-auto mt-4 px-4"
    in:fly={{ y: 50, duration: 500 }}
    out:fade
  >
    <div class="mb-10 flex items-start justify-between gap-3 w-full">
      <div class="pt-2.5 pl-3">
        <img src="/logo6.svg" alt="Company Logo" class="h-[1.4rem] w-auto" />
      </div>
      <ModelSelector index="home" />
    </div>
    <ChatInput on:message={handleUserMessage} />
    <Conversations />
  </div>
{/if}
