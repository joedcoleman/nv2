<script lang="ts">
  import { popup } from "@skeletonlabs/skeleton";
  import { appSettings } from "$lib/stores/SettingsStore";
  import { currentConversation } from "$lib/stores/ConversationStore";
  import type { PopupSettings } from "@skeletonlabs/skeleton";
  import { ListBox, ListBoxItem } from "@skeletonlabs/skeleton";
  import GridiconsDropdown from "~icons/gridicons/dropdown";

  export let index: string;

  let popupCombobox: PopupSettings = {
    event: "click",
    target: "popupCombobox" + index,
    placement: "bottom",
    closeQuery: ".listbox-item",
  };
</script>

<button
  class="btn btn-sm justify-between px-3 pt-1.5 {$currentConversation
    ? 'text-[13px] variant-ghost'
    : 'text-[15px]'}"
  use:popup={popupCombobox}
  on:click={() => console.log("Clicked!")}
>
  <span>{$appSettings.currentModel ?? "Trigger"}</span>
  <span><GridiconsDropdown /></span>
</button>
<div
  class="card variant-glass w-48 shadow-xl py-2 z-30 text-sm"
  data-popup="popupCombobox{index}"
>
  <ListBox rounded="rounded-none">
    {#each $appSettings.models as model}
      <ListBoxItem
        bind:group={$appSettings.currentModel}
        name="model"
        value={model}>{model}</ListBoxItem
      >
    {/each}
  </ListBox>
  <div class="arrow bg-surface-100-800-token" />
</div>
