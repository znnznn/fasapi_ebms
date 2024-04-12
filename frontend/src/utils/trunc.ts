export const trunc = (text: string, maxLenght: number) =>
    text?.length > maxLenght ? text?.substring(0, maxLenght - 3) + '...' : text
