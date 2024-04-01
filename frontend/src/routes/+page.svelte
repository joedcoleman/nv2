<script lang="ts">
  import type { PageData } from "./$types";
  import { onMount } from "svelte";
  import { fade, fly } from "svelte/transition";
  import { webSocketStore, isConnected } from "$lib/stores/WebSocketStore";
  import { appSettings, currentModel } from "$lib/stores/SettingsStore";
  import {
    currentConversation,
    currentMessage,
    conversationList,
  } from "$lib/stores/ConversationStore";
  import ChatInput from "$lib/components/ChatInput.svelte";
  import Conversations from "$lib/components/Conversations.svelte";
  import ChatWindow from "$lib/components/ChatWindow.svelte";
  import ModelSelector from "$lib/components/common/ModelSelector.svelte";

  export let data: PageData;

  onMount(() => {
    currentConversation.set(null);
    appSettings.set(data.settings.settings);
    conversationList.set(data.conversations);

    console.log($appSettings);
  });

  function handleUserMessage(event: CustomEvent<Message>) {
    const message = event.detail;
    webSocketStore.sendMessage(message);
  }
  $: comboboxValue = $currentModel;
  $: currentModel.set(comboboxValue);
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
      <ModelSelector bind:comboboxValue />
    </div>
    <ChatInput on:message={handleUserMessage} />
    <Conversations />
  </div>
{/if}
