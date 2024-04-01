import { writable } from 'svelte/store';

export const appSettings = writable<Settings>()

const isBrowser = typeof window !== 'undefined';

let initialValue = 'Claude Haiku';

if (isBrowser && localStorage.getItem('currentModel')) {
  initialValue = localStorage.getItem('currentModel') as string;
}

export const currentModel = writable<string>(initialValue);

if (isBrowser) {
  currentModel.subscribe(value => {
    localStorage.setItem('currentModel', value);
  });
}

