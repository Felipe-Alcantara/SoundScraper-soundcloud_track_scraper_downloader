import { cx } from '../../utils/cx'

function Input({ className = '', ...props }) {
  return (
    <input
      {...props}
      className={cx(
        'w-full h-10 rounded-xl bg-zinc-800/50 border border-white/10 px-3 text-sm text-white',
        'placeholder:text-zinc-400 input-glowing-border transition-all duration-300',
        'focus-visible:outline focus-visible:outline-2 focus-visible:outline-felixo-purple focus-visible:outline-offset-2',
        className,
      )}
    />
  )
}

export default Input
