export function scrollToBottom(node: HTMLElement, options?: { behavior?: ScrollBehavior }) {
  if (!node) return;
  const { behavior = 'auto' } = options || {};

  const scroll = () => {
    node.scrollTo({ top: node.scrollHeight, behavior });
  };

  scroll();

  return {
    update(newOptions?: { behavior?: ScrollBehavior }) {
      if (newOptions) {
        options = { ...options, ...newOptions };
      }
      scroll();
    },
  };
}