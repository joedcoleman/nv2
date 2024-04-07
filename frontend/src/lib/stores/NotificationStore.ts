import { writable } from "svelte/store";
import type { ToastSettings } from "@skeletonlabs/skeleton";

interface Notification {
  message: string;
  type: "success" | "error" | "info" | "warning" | null;
  settings?: Partial<ToastSettings>;
}

export const notificationStore = writable<Notification>({
  message: "",
  type: null,
  settings: {},
});

