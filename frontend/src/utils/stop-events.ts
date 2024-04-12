export const stopPropagation = <T extends React.MouseEvent>(e: T) => e.stopPropagation()

export const stopEvent = <T extends React.MouseEvent>(e: T) => {
    e.stopPropagation()
    e.preventDefault()
}
