import { cx } from '../../utils/cx'

export function Card({ className = '', ...props }) {
  return (
    <section
      {...props}
      className={cx(
        'rounded-3xl border border-white/10 bg-zinc-950/50 backdrop-blur-sm',
        className,
      )}
    />
  )
}

export function CardHeader({ className = '', ...props }) {
  return <header {...props} className={cx('p-5 border-b border-white/5', className)} />
}

export function CardContent({ className = '', ...props }) {
  return <div {...props} className={cx('p-5', className)} />
}

export function CardFooter({ className = '', ...props }) {
  return <footer {...props} className={cx('p-5 border-t border-white/5 flex items-center gap-3', className)} />
}

export function CardTitle({ className = '', ...props }) {
  return <h3 {...props} className={cx('text-base font-semibold', className)} />
}

export function CardDescription({ className = '', ...props }) {
  return <p {...props} className={cx('text-xs text-zinc-400', className)} />
}

