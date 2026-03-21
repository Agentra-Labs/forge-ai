import { put, del, list, head } from '@vercel/blob'

/**
 * Vercel Blob utility wrapper.
 * Mimics the hub:blob interface for easier migration.
 */
export const blob = {
  put: async (pathname: string, body: any, options: any = {}) => {
    return put(pathname, body, {
      access: 'public',
      ...options
    })
  },
  delete: async (url: string | string[]) => {
    return del(url)
  },
  list: async (options: any = {}) => {
    return list(options)
  },
  head: async (url: string) => {
    return head(url)
  }
}
