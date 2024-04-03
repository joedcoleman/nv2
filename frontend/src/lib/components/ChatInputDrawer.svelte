<script>
  import { appSettings } from "$lib/stores/SettingsStore";
  export let isDrawerOpen = false;
</script>

<div
  class="overflow-hidden variant-soft {isDrawerOpen ? 'h-[190px]' : 'h-0'}"
  style="transition: height 0.2s ease-in-out;"
>
  <div class="flex gap-6 p-5">
    <div class="flex-1 flex-col max-w-60">
      <label class="label mb-5">
        <span>Max Tokens</span>
        <input
          bind:value={$appSettings.maxTokens}
          type="number"
          class="input"
          max="300000"
        />
      </label>
      <label class="label">
        <span>Temperature</span>
        <input bind:value={$appSettings.temperature} type="range" max="100" />
      </label>
    </div>
    <div class="flex-1">
      <label class="label">
        <span>Custom Instructions</span>
        <textarea
          bind:value={$appSettings.customInstructions}
          class="textarea"
          rows="4"
          placeholder="Lorem ipsum dolor sit amet consectetur adipisicing elit."
        />
      </label>
    </div>
  </div>
</div>
