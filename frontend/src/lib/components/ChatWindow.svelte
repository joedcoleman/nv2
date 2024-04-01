<script lang="ts">
  import { popup } from "@skeletonlabs/skeleton";
  import type { PopupSettings } from "@skeletonlabs/skeleton";
  import { beforeUpdate, afterUpdate, onMount, tick } from "svelte";
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import { currentConversation } from "$lib/stores/ConversationStore";
  import { webSocketStore } from "$lib/stores/WebSocketStore";
  import { currentModel } from "$lib/stores/SettingsStore";
  import { scrollToBottom } from "$lib/actions/scrollToBottom";
  import ChatInput from "$lib/components/ChatInput.svelte";
  import MessageView from "$lib/components/MessageView.svelte";
  import PajamasGoBack from "~icons/pajamas/go-back";
  import ModelSelector from "$lib/components/common/ModelSelector.svelte";

  $: currentMessages = $currentConversation?.messages || [];
  $: userSentLastMessage =
    currentMessages.slice(-1)[0]?.role === "user" ?? false;

  let chatWindow: HTMLElement;
  let autoscroll: boolean;
  const threshold = 50;

  beforeUpdate(() => {
    autoscroll =
      userSentLastMessage ||
      (chatWindow &&
        chatWindow.offsetHeight + chatWindow.scrollTop >
          chatWindow.scrollHeight - threshold);
  });

  afterUpdate(async () => {
    await tick();
    if (chatWindow && autoscroll) {
      scrollToBottom(chatWindow, { behavior: "smooth" });
    }
  });

  function handleUserMessage(event: CustomEvent<Message>) {
    const message = event.detail;
    webSocketStore.sendMessage(message);
  }

  function handleBackClick() {
    if ($page.url.pathname === "/") {
      currentConversation.set(null);
    } else {
      goto("/");
    }
  }

  $: comboboxValue = $currentModel;
  $: currentModel.set(comboboxValue);
</script>

<div class="flex flex-col h-full max-w-full">
  <header
    class="absolute top-0 left-0 right-0 bg-surface-700 bg-opacity-30 backdrop-blur-md py-2 px-4 z-10 flex items-center gap-3"
  >
    <div class="flex items-center shrink-0">
      <button on:click={handleBackClick} type="button" class="btn p-0 text-lg"
        ><PajamasGoBack /></button
      >
    </div>
    <div class="flex grow items-center truncate">
      {$currentConversation?.title || "New conversation"}
    </div>
    <div class="flex items-center shrink-0">
      <ModelSelector bind:comboboxValue />
    </div>
  </header>
  <div
    class="flex flex-col overflow-y-auto gap-3 p-4 grow leading-7 pt-14"
    bind:this={chatWindow}
  >
    {#each currentMessages as message}
      <MessageView {message} />
    {/each}
  </div>
  <ChatInput on:message={handleUserMessage} />
</div>
