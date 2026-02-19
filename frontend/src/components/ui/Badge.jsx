import { cx } from '../../utils/cx'

function Badge({ className = '', ...props }) {
  return (
    <span
      {...props}
      className={cx(
        'inline-flex items-center rounded-full px-3 py-1 text-xs font-medium border border-white/10',
        className,
      )}
    />
  )
}

export default Badge

