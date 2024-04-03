<script lang="ts">
  import { onMount } from "svelte";
  import { fade, fly } from "svelte/transition";
  import { webSocketStore, isConnected } from "$lib/stores/WebSocketStore";
  import { currentConversation } from "$lib/stores/ConversationStore";
  import ChatInput from "$lib/components/ChatInput.svelte";
  import Conversations from "$lib/components/Conversations.svelte";
  import ChatWindow from "$lib/components/ChatWindow.svelte";
  import ModelSelector from "$lib/components/common/ModelSelector.svelte";

  onMount(() => {
    currentConversation.set(null);
  });

  function handleUserMessage(event: CustomEvent<Message>) {
    const message = event.detail;
    webSocketStore.sendMessage(message);
  }
</script>

{#if $currentConversation}
  <ChatWindow />
{:else}
  <div
    class="h-full flex flex-col justify-start items-center max-w-xl mx-auto mt-4 px-4"
    in:fly={{ y: 50, duration: 500 }}
    out:fade
  >
    <div class="mb-12 flex items-center justify-between gap-3 w-full">
      <div>
        <button
          type="button"
          class="btn btn-sm variant-glass flex items-center"
        >
          <div
            class="w-2 h-2 rounded-full {$isConnected
              ? 'bg-success-500'
              : 'bg-error-500'}"
          ></div>
          <div class="text-xs">
            {$isConnected ? "Connected" : "Disconnected"}
          </div>
        </button>
      </div>
      <ModelSelector index="home" />
    </div>
    <ChatInput on:message={handleUserMessage} />
    <Conversations />
  </div>
{/if}
