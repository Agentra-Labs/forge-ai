import { useToast } from '~/composables/useToast'

interface BlobResult {
    pathname: string
    url?: string
    contentType?: string
    size: number
}

function createObjectUrl(file: File): string {
    return URL.createObjectURL(file)
}

function fileToInput(file: File): HTMLInputElement {
    const dataTransfer = new DataTransfer()
    dataTransfer.items.add(file)

    const input = document.createElement('input')
    input.type = 'file'
    input.files = dataTransfer.files

    return input
}

type FileUploadOptions = {
    accept: string
    multiple: boolean
    onUpdate: (files: File[]) => void | Promise<void>
}

function useLocalFileUpload(options: FileUploadOptions) {
    const dropzoneRef = ref<HTMLElement | null>(null)
    const isDragging = ref(false)
    let inputEl: HTMLInputElement | null = null

    function handleFiles(fileList: FileList | null) {
        const files = fileList ? Array.from(fileList) : []
        if (files.length === 0) {
            return
        }

        void options.onUpdate(files)
    }

    function createInput() {
        if (!import.meta.client) {
            return null
        }

        if (inputEl) {
            return inputEl
        }

        inputEl = document.createElement('input')
        inputEl.type = 'file'
        inputEl.accept = options.accept
        inputEl.multiple = options.multiple
        inputEl.style.display = 'none'
        inputEl.addEventListener('change', () => {
            handleFiles(inputEl?.files ?? null)
            if (inputEl) {
                inputEl.value = ''
            }
        })
        document.body.appendChild(inputEl)

        return inputEl
    }

    function open() {
        const input = createInput()
        input?.click()
    }

    function onDragEnter(event: DragEvent) {
        // Only trigger if dragging actual files, not text/elements
        if (event.dataTransfer?.types.includes('Files')) {
            event.preventDefault()
            isDragging.value = true
        }
    }

    function onDragOver(event: DragEvent) {
        if (event.dataTransfer?.types.includes('Files')) {
            event.preventDefault()
            event.dataTransfer.dropEffect = 'copy'
            isDragging.value = true
        }
    }

    function onDragLeave(event: DragEvent) {
        // Only preventDefault and change state if we were actually in a dragging state
        if (isDragging.value) {
            event.preventDefault()
            // Only set isDragging to false if we're actually leaving the dropzone, 
            // not just moving into a child element.
            if (event.relatedTarget === null || (event.currentTarget && ! (event.currentTarget as HTMLElement).contains(event.relatedTarget as Node))) {
                isDragging.value = false
            }
        }
    }

    function onDrop(event: DragEvent) {
        if (event.dataTransfer?.types.includes('Files')) {
            event.preventDefault()
            isDragging.value = false
            handleFiles(event.dataTransfer?.files ?? null)
        }
    }

    function attach(el: HTMLElement | null) {
        if (!el) {
            return
        }

        el.addEventListener('dragenter', onDragEnter)
        el.addEventListener('dragover', onDragOver)
        el.addEventListener('dragleave', onDragLeave)
        el.addEventListener('drop', onDrop)
    }

    function detach(el: HTMLElement | null) {
        if (!el) {
            return
        }

        el.removeEventListener('dragenter', onDragEnter)
        el.removeEventListener('dragover', onDragOver)
        el.removeEventListener('dragleave', onDragLeave)
        el.removeEventListener('drop', onDrop)
    }

    watch(dropzoneRef, (next, prev) => {
        detach(prev)
        attach(next)
    })

    onBeforeUnmount(() => {
        detach(dropzoneRef.value)
        if (inputEl) {
            inputEl.remove()
            inputEl = null
        }
    })

    return {
        dropzoneRef,
        isDragging,
        open
    }
}

export function useFileUploadWithStatus(chatId: string) {
    const files = ref<FileWithStatus[]>([])
    const toast = useToast()
    const { isLoaded, isSignedIn } = useAuth()
    const canUpload = computed(() => isLoaded.value && isSignedIn.value)

    const { csrf, headerName } = useCsrf()

    const upload = useUpload(`/api/upload/${chatId}`, {
        method: 'PUT',
        headers: { [headerName]: csrf }
    })

    async function uploadFiles(newFiles: File[]) {
        if (!canUpload.value) {
            toast.add({
                title: 'Sign in required',
                description: 'Sign in with Google to upload files.',
                icon: 'lucide:log-in',
                color: 'warning'
            })
            return
        }

        const filesWithStatus: FileWithStatus[] = newFiles.map(file => ({
            file,
            id: crypto.randomUUID(),
            previewUrl: createObjectUrl(file),
            status: 'uploading' as const
        }))

        files.value = [...files.value, ...filesWithStatus]

        const uploadPromises = filesWithStatus.map(async (fileWithStatus) => {
            const index = files.value.findIndex(f => f.id === fileWithStatus.id)
            if (index === -1) return

            try {
                const input = fileToInput(fileWithStatus.file)
                const response = await upload(input) as BlobResult | BlobResult[] | undefined

                if (!response) {
                    throw new Error('Upload failed')
                }

                const result = Array.isArray(response) ? response[0] : response

                if (!result) {
                    throw new Error('Upload failed')
                }

                files.value[index] = {
                    ...files.value[index]!,
                    status: 'uploaded',
                    uploadedUrl: result.url,
                    uploadedPathname: result.pathname
                }
            } catch (error) {
                const errorMessage = (error as { data?: { message?: string } }).data?.message
                    || (error as Error).message
                    || 'Upload failed'
                toast.add({
                    title: 'Upload failed',
                    description: errorMessage,
                    icon: 'lucide:alert-circle',
                    color: 'error'
                })
                files.value[index] = {
                    ...files.value[index]!,
                    status: 'error',
                    error: errorMessage
                }
            }
        })

        await Promise.allSettled(uploadPromises)
    }

    const { dropzoneRef, isDragging, open } = useLocalFileUpload({
        accept: FILE_UPLOAD_CONFIG.acceptPattern,
        multiple: true,
        onUpdate: uploadFiles
    })

    const isUploading = computed(() =>
        files.value.some(f => f.status === 'uploading')
    )

    const uploadedFiles = computed(() =>
        files.value
            .filter(f => f.status === 'uploaded' && f.uploadedUrl)
            .map(f => ({
                type: 'file' as const,
                mediaType: f.file.type,
                url: f.uploadedUrl!
            }))
    )

    function removeFile(id: string) {
        const file = files.value.find(f => f.id === id)
        if (!file) return

        URL.revokeObjectURL(file.previewUrl)
        files.value = files.value.filter(f => f.id !== id)

        if (file.status === 'uploaded' && file.uploadedPathname) {
            $fetch(`/api/upload/${file.uploadedPathname}` as string, {
                method: 'DELETE',
                headers: { [headerName]: csrf }
            }).catch((error) => {
                console.error('Failed to delete file from blob:', error)
            })
        }
    }

    function clearFiles() {
        if (files.value.length === 0) return
        files.value.forEach(fileWithStatus => URL.revokeObjectURL(fileWithStatus.previewUrl))
        files.value = []
    }

    onUnmounted(() => {
        clearFiles()
    })

    return {
        dropzoneRef,
        isDragging,
        open,
        files,
        isUploading,
        uploadedFiles,
        addFiles: uploadFiles,
        removeFile,
        clearFiles
    }
}
