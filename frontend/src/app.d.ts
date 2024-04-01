import 'unplugin-icons/types/svelte'

// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
// and what to do when importing types
declare namespace App {
	// interface Locals {}
	// interface PageData {}
	// interface Error {}
	// interface Platform {}
}

declare module 'markdown-it-katex' {
	import MarkdownIt from 'markdown-it';
  
	interface KatexOptions {
	  throwOnError?: boolean;
	  errorColor?: string;
	  // Add more options if needed
	}
  
	export default function markdownItKatex(md: MarkdownIt, options?: KatexOptions): void;
  }