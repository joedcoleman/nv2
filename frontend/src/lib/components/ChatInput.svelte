<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import { scale } from "svelte/transition";
  import { quintOut } from "svelte/easing";
  import {
    currentConversation,
    currentMessage,
    previousMessage,
  } from "$lib/stores/ConversationStore";
  import { v4 as uuidv4 } from "uuid";
  import { appSettings } from "$lib/stores/SettingsStore";
  import { isConnected } from "$lib/stores/WebSocketStore";
  import { FileButton } from "@skeletonlabs/skeleton";
  import GridiconsAddImage from "~icons/gridicons/add-image";
  import MingcuteSendPlaneFill from "~icons/mingcute/send-plane-fill";
  import MingcuteArrowsUpLine from "~icons/mingcute/arrows-up-line";
  import MingcuteArrowsDownLine from "~icons/mingcute/arrows-down-line";
  import ChatInputDrawer from "./ChatInputDrawer.svelte";
  import { notificationStore } from "$lib/stores/NotificationStore";

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
        navigator.userAgent,
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
      notificationStore.set({
        message: "WebSocket not connected. Refresh and try again.",
        type: "error",
      });
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

      previousMessage.set($currentMessage);

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
      10,
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

  async function captureScreen() {
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    const video = document.createElement("video");

    try {
      // Request access to the screen capture
      const captureStream = await navigator.mediaDevices.getDisplayMedia();

      // Play the video to load the data
      video.srcObject = captureStream;
      video.play();

      // Draw the video frame to the canvas after the video has enough data
      video.onloadedmetadata = () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context?.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);

        // Convert the canvas to a data URL
        const frame = canvas.toDataURL("image/png");

        // Stop all video tracks
        captureStream.getTracks().forEach((track) => track.stop());

        // Here you can handle the screenshot data URL (e.g., display it, send to server)
        console.log(frame); // Or display in an <img> element, etc.
      };
    } catch (err) {
      console.error("Error capturing screen:", err);
    }
  }
</script>

<div class="flex flex-col p-2 pt-1 w-full">
  <div
    class="flex rounded-md shadow-sm ring-0 {$currentConversation
      ? 'bg-tertiary-200/10 border-0 mx-auto max-w-3xl w-full'
      : 'bg-transparent border border-surface-400'}"
  >
    {#if $currentConversation}
      <button
        on:click={() => (isDrawerOpen = !isDrawerOpen)}
        class="inline-flex items-start rounded-l-md pl-3 pr-2.5 py-2 my-2 text-surface-200 border-r border-surface-400/80"
      >
        {#if isDrawerOpen}
          <MingcuteArrowsDownLine />
        {:else}
          <MingcuteArrowsUpLine />
        {/if}
      </button>
    {/if}
    <textarea
      bind:value={$currentMessage}
      bind:this={textareaElement}
      class="rounded-l-md block bg-transparent placeholder-surface-300 w-full min-w-0 flex-1 border-0 ring-0 focus:ring-0 focus:border-0 resize-none {$currentConversation
        ? 'py-3'
        : 'py-4 pl-5'}"
      name="prompt"
      id="prompt"
      placeholder="Write a message..."
      rows={$currentConversation ? 1 : 4}
      spellcheck="false"
      on:input={adjustTextareaHeight}
      on:keydown={handleKeyDown}
      disabled={!$isConnected}
    />
    <div
      class="rounded-r-md h-full bg-transparent flex items-start justify-center {$currentConversation
        ? 'p-2 gap-1.5'
        : 'p-4 gap-2'}"
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
          button="btn-icon btn-icon-sm {$isConnected
            ? 'variant-filled-secondary'
            : 'bg-surface-500'}"
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
          class="btn-icon btn-icon-sm flex items-center {$isConnected
            ? 'variant-filled-primary'
            : 'bg-surface-500'}"
        >
          <MingcuteSendPlaneFill />
        </button>
      {/if}
    </div>
  </div>
  <ChatInputDrawer {isDrawerOpen} />
</div>
