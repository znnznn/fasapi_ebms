export interface OpenClose {
    open: boolean
    setOpen: React.Dispatch<React.SetStateAction<boolean>>
}

export type ButtonEvent = React.MouseEvent<HTMLButtonElement, MouseEvent>
export type InputEvent = React.ChangeEvent<HTMLInputElement>
export type DivEvent = React.ChangeEvent<HTMLDivElement>
