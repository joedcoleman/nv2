<script lang="ts">
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
  import { clipboard, Toast, getToastStore } from "@skeletonlabs/skeleton";
  initializeStores();
  storePopup.set({ computePosition, autoUpdate, offset, shift, flip, arrow });

  onMount(() => {
    let subscription = webSocketStore.subscribe(() => {});

    return () => {
      subscription();
    };
  });
</script>

<Toast />
<slot />
