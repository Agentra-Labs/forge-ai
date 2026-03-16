type ShortcutMap = Record<string, () => void>

export function defineShortcuts(shortcuts: ShortcutMap) {
  if (!import.meta.client) {
    return
  }

  onMounted(() => {
    const handler = (event: KeyboardEvent) => {
      if (event.metaKey || event.ctrlKey || event.altKey) {
        return
      }

      const key = event.key.toLowerCase()
      const callback = shortcuts[key]
      if (!callback) {
        return
      }

      const target = event.target as HTMLElement | null
      const tagName = target?.tagName?.toLowerCase()
      if (tagName === 'input' || tagName === 'textarea' || target?.isContentEditable) {
        return
      }

      event.preventDefault()
      callback()
    }

    window.addEventListener('keydown', handler)
    onBeforeUnmount(() => {
      window.removeEventListener('keydown', handler)
    })
  })
}

export function extractShortcuts(shortcuts: ShortcutMap) {
  return Object.keys(shortcuts)
}
