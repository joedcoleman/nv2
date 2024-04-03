<script lang="ts">
  let username = "";
  let password = "";
  let showError = false;

  async function handleLogin(event: SubmitEvent) {
    event.preventDefault(); // Prevent page reload

    // Create a FormData object
    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    // Send credentials to FastAPI backend
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/auth`, {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      const { token } = await response.json();
      document.cookie = `auth_token=${token}; path=/`;
      window.location.href = "/";
    } else {
      showError = true;
      console.error("Login failed");
    }
  }
</script>

<div class="flex flex-col items-center justify-start min-h-screen mt-16">
  <div class="w-full max-w-xs">
    <form
      on:submit={handleLogin}
      class="variant-soft shadow-md rounded px-8 pt-6 pb-8 mb-4"
    >
      <div class="mb-4">
        <label class="block text-sm font-bold mb-2" for="username">
          Username
        </label>
        <input
          bind:value={username}
          class="text-surface-600 shadow appearance-none border rounded w-full py-2 px-3 leading-tight focus:outline-none focus:shadow-outline"
          id="username"
          type="text"
          placeholder="Username"
        />
      </div>
      <div class="mb-4">
        <label class="block text-sm font-bold mb-2" for="password">
          Password
        </label>
        <input
          bind:value={password}
          class="shadow appearance-none text-surface-600 border rounded w-full py-2 px-3 mb-3 leading-tight focus:outline-none focus:shadow-outline"
          id="password"
          type="password"
          placeholder="**********"
        />
      </div>
      <div class="flex items-center justify-between">
        <button class="btn variant-ghost-tertiary" type="submit">
          Sign In
        </button>
      </div>
    </form>
  </div>
  {#if showError}
    <div class="mt-2">Incorrect username or password!</div>
  {/if}
</div>
