export const unwrap = response => response.data

export const unwrapList = response => ({ items: response.data, meta: response.meta || {} })
