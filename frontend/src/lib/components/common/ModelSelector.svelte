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

<div></div>
<button
  class="btn btn-sm justify-end px-3 pt-1.5 text-sm w-40"
  use:popup={popupCombobox}
>
  <span>{$appSettings.currentModel ?? "Model"}</span>
  <span><GridiconsDropdown /></span>
</button>
<div
  class="card w-40 shadow-xl py-2 z-30 text-sm rounded-md variant-glass-secondary"
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
</div>
