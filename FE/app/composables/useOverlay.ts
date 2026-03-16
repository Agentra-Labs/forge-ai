type OverlayCreateOptions = {
  props?: {
    title?: string
    description?: string
  }
}

export function useOverlay() {
  function create(_component: unknown, options?: OverlayCreateOptions) {
    return {
      open() {
        const message = [options?.props?.title, options?.props?.description]
          .filter(Boolean)
          .join('\n\n')

        const accepted = import.meta.client
          ? window.confirm(message || 'Are you sure?')
          : false

        return {
          result: Promise.resolve(accepted)
        }
      }
    }
  }

  return { create }
}
