declare module 'markdown-it-katex' {
    import MarkdownIt from 'markdown-it';
  
    interface KatexOptions {
      throwOnError?: boolean;
      errorColor?: string;
      // Add more options if needed
    }
  
    export default function markdownItKatex(md: MarkdownIt, options?: KatexOptions): void;
  }