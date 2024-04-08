<script lang="ts">
  import { conversationList } from "$lib/stores/ConversationStore";
  import { goto } from "$app/navigation";
  import { formatDistanceToNow } from "date-fns";

  function handleConversationClick(conversationId: string) {
    goto(`/chat/${conversationId}`);
  }

  function formatRelativeTime(dateString: string) {
    const date = new Date(dateString);
    return formatDistanceToNow(date, { addSuffix: true });
  }

  function toLocalTime(dateString: string) {
    const date = new Date(dateString);
    return date.toLocaleString();
  }
</script>

{#if $conversationList}
  <div class="text-surface-300 mb-6 text-lg mt-10">Recent chats</div>
  <div class="text-center w-full h-full overflow-y-scroll">
    <ul class="divide-y divide-surface-400/40 px-2">
      {#each $conversationList
        .sort((a, b) => {
          const dateA = a.updated_at ? new Date(a.updated_at) : new Date(0);
          const dateB = b.updated_at ? new Date(b.updated_at) : new Date(0);
          return dateB.getTime() - dateA.getTime();
        })
        .slice(0, 5) as conversation}
        {#if conversation.messages.length > 0 && conversation.messages[conversation.messages.length - 1].content[0].text.trim() !== ""}
          <li
            on:click={() => handleConversationClick(conversation.id)}
            class="p-4 cursor-pointer bg-transparent text-surface-100 hover:variant-glass-surface"
          >
            <div class="flex-auto truncate max-w-2xl text-left">
              {conversation.title || "New conversation"}
            </div>
            <div class="text-surface-400 text-sm text-left">
              {#if conversation.updated_at}
                {formatRelativeTime(toLocalTime(conversation.updated_at))}
              {/if}
            </div>
          </li>
        {/if}
      {/each}
    </ul>
  </div>
{/if}
