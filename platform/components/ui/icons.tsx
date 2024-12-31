import { LucideProps, Loader2, Copy, LogOut, Plus, Settings, ArrowRight } from "lucide-react"

export type IconProps = LucideProps

export const Icons = {
  spinner: Loader2,
  copy: Copy,
  logout: LogOut,
  plus: Plus,
  settings: Settings,
  arrowRight: ArrowRight,
  microsoft: (props: IconProps) => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 23 23"
      width="24"
      height="24"
      {...props}
    >
      <path fill="#f35325" d="M1 1h10v10H1z"/>
      <path fill="#81bc06" d="M12 1h10v10H12z"/>
      <path fill="#05a6f0" d="M1 12h10v10H1z"/>
      <path fill="#ffba08" d="M12 12h10v10H12z"/>
    </svg>
  ),
}