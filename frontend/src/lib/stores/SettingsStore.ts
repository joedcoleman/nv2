import type {Writable} from 'svelte/store';
import { localStorageStore } from '@skeletonlabs/skeleton';

let initialSettings = { models: ['GPT-4', 'Claude Haiku'], currentModel: 'GPT-4', customInstructions: 'You are a helpful assistant.', maxTokens: 5000, temperature: 70 }

export const appSettings: Writable<Settings> = localStorageStore('appSettings', initialSettings);
