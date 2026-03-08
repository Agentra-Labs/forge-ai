import { MODELS } from '#shared/utils/models'

export function useModels() {
    const model = useCookie<string>('model', { default: () => 'amazon/nova-lite-v1' })

    return {
        models: MODELS,
        model
    }
}
