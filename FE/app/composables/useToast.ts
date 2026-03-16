type ToastInput = {
  title?: string
  description?: string
  icon?: string
  color?: string
  duration?: number
}

type Toast = ToastInput & {
  id: string
  createdAt: number
}

export function useToast() {
  const toastStore = useState<Toast[]>('toast-store', () => [])

  function add(input: ToastInput) {
    toastStore.value.push({
      id: crypto.randomUUID(),
      createdAt: Date.now(),
      ...input
    })

    // Keep a bounded in-memory list during migration away from Nuxt UI.
    if (toastStore.value.length > 50) {
      toastStore.value.shift()
    }
  }

  return { add }
}
