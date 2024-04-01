<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import { currentConversation } from "$lib/stores/ConversationStore";
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import { v4 as uuidv4 } from "uuid";
  import MingcuteArrowsUpFill from "~icons/mingcute/arrows-up-fill";
  import CarbonNewTab from "~icons/carbon/new-tab";

  let isDrawerOpen = false;
  let currentMessage = "";
  let textareaElement: HTMLTextAreaElement;

  const dispatch = createEventDispatcher<{
    message: Message;
  }>();

  onMount(() => {
    textareaElement.focus();
  });

  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  function handleBackClick() {
    if ($page.url.pathname === "/") {
      currentConversation.set(null);
    } else {
      goto("/");
    }
  }

  function sendMessage() {
    if (currentMessage.trim() !== "") {
      const newMessage: Message = {
        id: uuidv4(),
        role: "user",
        content: currentMessage.trim(),
        conversation_id: $currentConversation?.id || uuidv4(),
      };
      dispatch("message", newMessage);
      currentMessage = "";
      setTimeout(() => {
        adjustTextareaHeight();
      }, 0);
      adjustTextareaHeight();
    }
  }

  function adjustTextareaHeight() {
    textareaElement.style.height = "auto";
    const baseHeight = 28;
    let desiredHeight = textareaElement.scrollHeight;
    const maxHeight = baseHeight * 4;
    textareaElement.style.height = `${Math.min(desiredHeight, maxHeight)}px`;
  }
</script>

<div
  class="flex flex-col p-2 pt-1 {!$currentConversation
    ? 'w-full max-w-md'
    : ''}"
>
  <div class="variant-soft flex rounded-md shadow-sm border-0 ring-0">
    {#if $currentConversation}
      <button
        on:click={handleBackClick}
        class="inline-flex items-start rounded-l-md px-3 pt-3.5 variant-soft sm:text-sm"
        ><CarbonNewTab /></button
      >
      <!-- <button
        on:click={() => (isDrawerOpen = !isDrawerOpen)}
        class="inline-flex items-start rounded-l-md px-3 pt-3.5 variant-soft sm:text-sm"
        ><MingcuteArrowsUpFill /></button
      > -->
    {/if}
    <textarea
      bind:value={currentMessage}
      bind:this={textareaElement}
      class="block variant-glass w-full min-w-0 flex-1 rounded-none rounded-r-md border-0 ring-0 focus:ring-0 focus:border-0 py-2.5"
      name="prompt"
      id="prompt"
      placeholder="Write a message..."
      rows={$currentConversation ? 1 : 4}
      on:input={adjustTextareaHeight}
      on:keydown={handleKeyDown}
    />
  </div>
  <div
    class="drawer-content {isDrawerOpen ? 'drawer-open' : ''}"
    style="height: {isDrawerOpen
      ? '150px'
      : '0'}; transition: height 0.2s ease-in-out;"
  >
    <div
      class="drawer-inner flex gap-5 items-center justify-center w-full p-4 mt-2 rounded-lg h-full"
      style="background-image: url('https://images.unsplash.com/photo-1581937019650-bb34507b7d64?q=80&w=1335&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'); background-size: cover; background-position: center;"
    >
      <div>
        <label class="label">
          <span>Instructions</span>
          <textarea
            class="textarea variant-glass"
            rows="1"
            placeholder="You are a helpful assistant."
          />
        </label>
      </div>
      <div>
        <label class="label">
          <span>Model</span>
          <select class="select variant-glass">
            <option value="1">GPT-4</option>
            <option value="2">Claude 3 Opus</option>
            <option value="3">Claude 3 Haiku</option>
            <option value="4">Gemini Pro 1.0</option>
          </select>
        </label>
      </div>
    </div>
  </div>
</div>

<style>
  .drawer-content {
    overflow: hidden;
  }
  .drawer-open {
    height: 150px; /* Adjust the height as needed */
  }
</style>
