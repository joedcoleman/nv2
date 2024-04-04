<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import { scale } from "svelte/transition";
  import { quintOut } from "svelte/easing";
  import {
    currentConversation,
    currentMessage,
  } from "$lib/stores/ConversationStore";
  import { v4 as uuidv4 } from "uuid";
  import { appSettings } from "$lib/stores/SettingsStore";
  import { isConnected } from "$lib/stores/WebSocketStore";
  import { FileButton, getToastStore } from "@skeletonlabs/skeleton";
  import type { ToastSettings } from "@skeletonlabs/skeleton";
  import GridiconsAddImage from "~icons/gridicons/add-image";
  import MingcuteSendPlaneFill from "~icons/mingcute/send-plane-fill";
  import MingcuteArrowsUpFill from "~icons/mingcute/arrows-up-fill";
  import MingcuteArrowsDownFill from "~icons/mingcute/arrows-down-fill";
  import ChatInputDrawer from "./ChatInputDrawer.svelte";

  const toastStore = getToastStore();
  let textareaElement: HTMLTextAreaElement;
  let images: FileList | undefined;
  let thumbnailURL: string | undefined;

  let isDrawerOpen = false;

  const dispatch = createEventDispatcher<{
    message: Message;
  }>();

  onMount(() => {
    if (
      !/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
        navigator.userAgent
      )
    ) {
      textareaElement.focus();
    }
  });

  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  async function sendMessage() {
    if (!$isConnected) {
      const t: ToastSettings = {
        message: "WebSocket not connected. Refresh and try again.",
        background: "variant-filled-error",
      };
      toastStore.trigger(t);
      return;
    }
    if ($currentMessage.trim() !== "" || (images && images?.length > 0)) {
      const newMessage: Message = {
        id: uuidv4(),
        role: "user",
        content: [],
        conversation_id: $currentConversation?.id || uuidv4(),
        meta_data: {
          llm: {
            model: $appSettings.currentModel,
            instructions: $appSettings.customInstructions,
            max_tokens: $appSettings.maxTokens,
            temperature: $appSettings.temperature,
          },
        },
      };

      if (images && images?.length > 0) {
        const imageFile = images[0];
        const base64Image = await convertImageToBase64(imageFile);
        newMessage.content.push({
          type: "image_url",
          image_url: {
            url: base64Image,
          },
        });
      }

      if ($currentMessage.trim() !== "") {
        newMessage.content.push({
          type: "text",
          text: $currentMessage.trim(),
        });
      }

      dispatch("message", newMessage);
      $currentMessage = "";
      images = undefined;

      setTimeout(() => {
        adjustTextareaHeight();
      }, 0);
      adjustTextareaHeight();
    }
  }

  function adjustTextareaHeight() {
    const baseHeight = 28;
    let maxHeight = baseHeight * 15;
    if ($currentConversation) {
      maxHeight = baseHeight * 4;
    }

    let currentHeight = parseInt(
      window.getComputedStyle(textareaElement).height,
      10
    );

    if (currentHeight > maxHeight) {
      return;
    }

    textareaElement.style.height = "auto";
    let desiredHeight = textareaElement.scrollHeight;
    textareaElement.style.height = `${Math.min(desiredHeight, maxHeight)}px`;
  }

  async function convertImageToBase64(imageFile: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const base64String = reader.result as string;
        const base64Prefix = `data:${imageFile.type};base64,`;
        const fullBase64String = base64Prefix + base64String.split(",")[1];
        thumbnailURL = fullBase64String;
        resolve(fullBase64String);
      };
      reader.onerror = (error) => {
        reject(error);
      };
      reader.readAsDataURL(imageFile);
    });
  }
</script>

<div class="flex flex-col p-2 pt-1 w-full">
  <div class="variant-soft flex rounded-md shadow-sm border-0 ring-0">
    {#if $currentConversation}
      <button
        on:click={() => (isDrawerOpen = !isDrawerOpen)}
        class="inline-flex items-start rounded-l-md px-3 pt-4 variant-soft"
      >
        {#if isDrawerOpen}
          <MingcuteArrowsDownFill />
        {:else}
          <MingcuteArrowsUpFill />
        {/if}
      </button>
    {/if}
    <textarea
      bind:value={$currentMessage}
      bind:this={textareaElement}
      class="rounded-l-md block variant-glass w-full min-w-0 flex-1 border-0 ring-0 focus:ring-0 focus:border-0 resize-none {$currentConversation
        ? 'py-3'
        : 'p-4'}"
      name="prompt"
      id="prompt"
      placeholder="Write a message..."
      rows={$currentConversation ? 1 : 4}
      spellcheck="false"
      on:input={adjustTextareaHeight}
      on:keydown={handleKeyDown}
    />
    <div
      class="rounded-r-md h-full variant-glass flex items-start justify-center p-2 gap-2"
    >
      {#if thumbnailURL}
        <div class="relative">
          <img
            src={thumbnailURL}
            alt="Thumbnail"
            class="h-8 w-8 object-cover rounded"
          />
          <button
            on:click={() => {
              images = undefined;
              thumbnailURL = undefined;
            }}
            class="absolute top-0 right-0 variant-soft rounded-full w-3 h-3 flex items-center justify-center text-xs"
          >
            &times;
          </button>
        </div>
      {:else}
        <FileButton
          name="image"
          button="btn-icon btn-icon-sm variant-soft"
          bind:files={images}
          on:change={() => {
            if (images && images?.length > 0) {
              convertImageToBase64(images[0]);
            }
          }}
        >
          <GridiconsAddImage />
        </FileButton>
      {/if}
      {#if $currentMessage || (images && images?.length > 0) || !$currentConversation}
        <button
          on:click={sendMessage}
          in:scale={{
            duration: 300,
            opacity: 0.3,
            start: 0.3,
            easing: quintOut,
          }}
          type="button"
          class="btn-icon btn-icon-sm flex items-center bg-tertiary-500/50"
        >
          <MingcuteSendPlaneFill />
        </button>
      {/if}
    </div>
  </div>
  <ChatInputDrawer {isDrawerOpen} />
</div>
