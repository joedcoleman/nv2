<script lang="ts">
  import type { LayoutData, PageData } from "./$types";
  import { onMount, onDestroy } from "svelte";
  import { webSocketStore } from "$lib/stores/WebSocketStore";
  import {
    computePosition,
    autoUpdate,
    offset,
    shift,
    flip,
    arrow,
  } from "@floating-ui/dom";
  import "../app.postcss";
  import { storePopup } from "@skeletonlabs/skeleton";
  import { initializeStores } from "@skeletonlabs/skeleton";
  import { Toast } from "@skeletonlabs/skeleton";
  import { appSettings } from "$lib/stores/SettingsStore";
  import { conversationList } from "$lib/stores/ConversationStore";

  export let data: LayoutData;

  initializeStores();
  storePopup.set({ computePosition, autoUpdate, offset, shift, flip, arrow });

  onMount(() => {
    let subscription = webSocketStore.subscribe(() => {});

    return () => {
      subscription();
    };
  });

  $: {
    appSettings.update((settings) => {
      return { ...settings, models: data.settings.models };
    });
  }

  $: conversationList.set(data.conversations);
</script>

<Toast />

<slot />
