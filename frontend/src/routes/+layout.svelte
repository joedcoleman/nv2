<script lang="ts">
  import type { LayoutData } from "./$types";
  import { onMount } from "svelte";
  import { webSocketStore } from "$lib/stores/WebSocketStore";
  import { appSettings } from "$lib/stores/SettingsStore";
  import { conversationList } from "$lib/stores/ConversationStore";
  import { notificationStore } from "$lib/stores/NotificationStore";
  import type { ToastSettings } from "@skeletonlabs/skeleton";
  import {
    storePopup,
    initializeStores,
    Toast,
    getToastStore,
  } from "@skeletonlabs/skeleton";
  import {
    computePosition,
    autoUpdate,
    offset,
    shift,
    flip,
    arrow,
  } from "@floating-ui/dom";
  import "../app.postcss";

  initializeStores();
  storePopup.set({ computePosition, autoUpdate, offset, shift, flip, arrow });

  export let data: LayoutData;
  const toastStore = getToastStore();

  onMount(() => {
    const subscription = webSocketStore.subscribe(() => {});
    return () => {
      subscription();
    };
  });

  $: if ($notificationStore.message) {
    showNotification();
  }

  $: appSettings.update((settings) => {
    return { ...settings, models: data.settings.models };
  });

  $: conversationList.set(data.conversations);

  function showNotification() {
    const backgroundMap = {
      info: "variant-filled-secondary",
      error: "variant-filled-error",
      warning: "variant-filled-warning",
      success: "variant-filled-success",
    };

    const defaultOptions: ToastSettings = {
      message: $notificationStore?.message,
      background:
        backgroundMap[$notificationStore?.type || "info"] ||
        "variant-filled-secondary",
      ...$notificationStore?.settings,
    };

    toastStore.trigger(defaultOptions);
    notificationStore.set({
      message: "",
      type: null,
      settings: {},
    });
  }
</script>

<Toast />

<slot />
