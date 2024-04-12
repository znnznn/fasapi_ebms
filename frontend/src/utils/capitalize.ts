export const capitalize = (string: string) =>
    string?.replace(/\b\w/g, (char) => char?.toUpperCase())
