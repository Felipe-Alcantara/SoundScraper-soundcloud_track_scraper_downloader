import { cx } from '../../utils/cx'

const variantClasses = {
  default: 'bg-white text-black border-white/10 hover:bg-zinc-100',
  outline: 'bg-transparent text-white border-white/20 hover:bg-white/5',
  ghost: 'bg-transparent text-white border-transparent hover:bg-white/5',
  secondary: 'bg-zinc-800 text-white border-white/10 hover:bg-zinc-700',
}

const sizeClasses = {
  md: 'h-10 px-4',
  sm: 'h-9 px-3',
  icon: 'h-12 w-12 p-2',
}

function Button({
  variant = 'default',
  size = 'md',
  shimmer = false,
  className = '',
  children,
  ...props
}) {
  return (
    <button
      {...props}
      className={cx(
        'group relative inline-flex items-center justify-center gap-2 rounded-2xl text-sm font-medium',
        'transition-all duration-300 shadow-sm border disabled:opacity-45 disabled:cursor-not-allowed',
        variantClasses[variant],
        sizeClasses[size],
        className,
      )}
    >
      {shimmer && (
        <span className="pointer-events-none absolute inset-0 -translate-x-full group-hover:translate-x-[150%] transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/20 to-transparent" />
      )}
      <span className="relative z-10">{children}</span>
    </button>
  )
}

export default Button

