<script lang="ts">
  import { onMount, afterUpdate } from "svelte";
  import { fade } from "svelte/transition";
  import { clipboard, getToastStore } from "@skeletonlabs/skeleton";
  import type { ToastSettings } from "@skeletonlabs/skeleton";
  import MarkdownIt from "markdown-it";
  import markdownItKatex from "markdown-it-katex";
  import hljs from "highlight.js";
  import "highlight.js/styles/tokyo-night-dark.css";
  import TablerBrandOpenai from "~icons/tabler/brand-openai";
  import PajamasRetry from "~icons/pajamas/retry";
  import TablerClipboard from "~icons/tabler/clipboard";
  import AnthropicIcon from "./common/AnthropicIcon.svelte";
  import TablerBrandGoogleFilled from "~icons/tabler/brand-google-filled";
  import { isSelecting } from "$lib/stores/WebSocketStore";
  import { currentConversation } from "$lib/stores/ConversationStore";
  import { webSocketStore } from "$lib/stores/WebSocketStore";
  import MingcuteRightLine from "~icons/mingcute/right-line";
  import MingcuteLeftLine from "~icons/mingcute/left-line";
  import { appSettings } from "$lib/stores/SettingsStore";

  export let message: Message;

  const toastStore = getToastStore();

  function handleCopy() {
    console.log("Handling copy!");
    const t: ToastSettings = {
      message: "Message copied!",
      hideDismiss: true,
      timeout: 2000,
      background: "bg-tertiary-500/70",
      classes: "backdrop-blur-sm",
    };
    toastStore.trigger(t);
  }

  const md = new MarkdownIt({
    html: true,
    linkify: true,
    typographer: true,
    highlight: function (code: string, lang: string) {
      const language = hljs.getLanguage(lang) ? lang : "plaintext";
      const highlightedCode = hljs.highlight(code, { language }).value;
      const langClass = `language-${language}`;
      const copyButton = `<button class="copy-button absolute right-0 mr-2 mt-2 top-0 text-xs bg-gray-800 opacity-75 text-white py-1 px-2 rounded hover:bg-gray-700" data-code="${btoa(code)}">Copy</button>`;
      return `<pre class="hljs rounded-md px-5 py-4 overflow-x-auto relative">${copyButton}<code class="${langClass}">${highlightedCode}</code></pre>`;
    },
  });

  markdownItKatex(md, {
    throwOnError: false,
  });

  function renderContent(content: any[]) {
    let renderedContent = "";

    content.forEach((item) => {
      if (item.type === "text") {
        const sanitizedContent = md.render(item.text);
        renderedContent += sanitizedContent;
      } else if (item.type === "image_url") {
        renderedContent += `<img src="${item.image_url.url}" alt="Image" class="max-w-44 rounded-md">`;
      }
    });

    return renderedContent;
  }

  $: processedContent = renderContent(message.content);
  $: role = message.role;

  onMount(() => {
    addCopyButtonListeners();
  });

  afterUpdate(() => {
    addCopyButtonListeners();
  });

  function addCopyButtonListeners() {
    const copyButtons = document.querySelectorAll(".copy-button");
    copyButtons.forEach((button) => {
      button.removeEventListener("click", handleCopyClick);
      button.addEventListener("click", handleCopyClick);
    });
  }

  function handleCopyClick(event: Event) {
    const button = event.target as HTMLButtonElement;
    const code = atob(button.dataset.code!);
    navigator.clipboard.writeText(code).then(() => {
      const t: ToastSettings = {
        message: "Code copied!",
        hideDismiss: true,
        timeout: 2000,
        background: "bg-tertiary-500/70",
        classes: "backdrop-blur-sm",
      };
      toastStore.trigger(t);
    });
  }

  function handleSelectionStart() {
    isSelecting.set(true);
  }

  function handleSelectionEnd() {
    isSelecting.set(false);
  }

  function regenerateMessage() {
    message.content = [{ type: "text", text: "" }];
    message.meta_data.llm.model = $appSettings.currentModel;

    webSocketStore.sendMessage({
      id: crypto.randomUUID(),
      role: "command",
      content: "regenerate",
      conversation_id: $currentConversation?.id || crypto.randomUUID(),
      meta_data: {
        llm: { model: $appSettings.currentModel },
        message_to_regenerate: message.id,
      },
    });
  }

  let currentVersionIndex = 0;

  function showNextVersion() {
    if (currentVersionIndex < message.meta_data.versions.length - 1) {
      currentVersionIndex++;
      message.content = message.meta_data.versions[currentVersionIndex].content;
      message.meta_data.llm.model =
        message.meta_data.versions[currentVersionIndex].meta_data.llm.model;
    }
  }

  function showPreviousVersion() {
    if (currentVersionIndex > 0) {
      currentVersionIndex--;
      message.content = message.meta_data.versions[currentVersionIndex].content;
      message.meta_data.llm.model =
        message.meta_data.versions[currentVersionIndex].meta_data.llm.model;
    }
  }
</script>

<div
  class="flex items-start max-w-full gap-4"
  transition:fade={{ duration: 100 }}
  role="region"
  on:mousedown={handleSelectionStart}
  on:mouseup={handleSelectionEnd}
  on:touchstart={handleSelectionStart}
  on:touchend={handleSelectionEnd}
>
  <div
    class="card p-4 px-5 w-full overflow-x-auto space-y-3 font-light rounded-xl leading-8"
    class:variant-glass-surface={role === "assistant"}
    class:variant-glass={role === "user"}
  >
    {#if role === "assistant"}
      <div
        class="text-xs flex grow-0 w-full justify-between items-center font-semibold text-surface-400 fill-surface-400"
      >
        <div class="flex w-1/3 items-center justify-start gap-1.5">
          {#if ["GPT-4", "GPT-4-Turbo"].includes(message?.meta_data?.llm?.model)}
            <TablerBrandOpenai />
          {:else if ["Claude Opus", "Claude Haiku"].includes(message?.meta_data?.llm?.model)}
            <AnthropicIcon />
          {:else if ["Gemini Pro"].includes(message?.meta_data?.llm?.model)}
            <TablerBrandGoogleFilled />
          {/if}
          {message?.meta_data?.llm?.model}
        </div>
        {#if message?.meta_data?.versions.length > 1}
          <div class="flex w-1/3 items-center justify-center gap-2">
            <button
              class="btn p-0"
              on:click={showPreviousVersion}
              disabled={currentVersionIndex === 0}
            >
              <MingcuteLeftLine />
            </button>
            <span
              >{currentVersionIndex + 1} of {message.meta_data.versions
                .length}</span
            >

            <button
              class="btn p-0"
              on:click={showNextVersion}
              disabled={currentVersionIndex ===
                message.meta_data.versions.length - 1}
            >
              <MingcuteRightLine />
            </button>
          </div>
        {/if}
        <div class="flex w-1/3 gap-2 items-center justify-end">
          <button
            class="btn p-0"
            on:click={handleCopy}
            use:clipboard={message?.content[0].text}
          >
            <TablerClipboard />
          </button>
          <button class="btn p-0" on:click={regenerateMessage}>
            <PajamasRetry class="text-xs cursor-pointer" />
          </button>
        </div>
      </div>
    {/if}
    <div class="prose prose-invert max-w-2xl">
      {@html processedContent}
    </div>
  </div>
</div>
