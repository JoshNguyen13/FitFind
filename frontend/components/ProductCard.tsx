import type { Product } from '@/types'

export default function ProductCard({ product }: { product: Product }) {
  return (
    <div className="group flex flex-col">
      {/* Image */}
      <div className="aspect-3/4 bg-neutral-50 overflow-hidden mb-3">
        {product.image_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={product.image_url}
            alt={product.product_title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-neutral-300 text-xs tracking-widest uppercase">
            No Image
          </div>
        )}
      </div>

      {/* Info */}
      <div className="flex-1 flex flex-col gap-1 mb-3">
        {product.brand && (
          <p className="text-xs tracking-widest uppercase text-neutral-400">
            {product.brand}
          </p>
        )}
        <p className="text-sm font-light leading-snug line-clamp-2">
          {product.product_title}
        </p>
        <p className="text-sm tracking-wide">
          {product.price != null ? `$${product.price.toFixed(2)}` : 'See Price'}
        </p>
      </div>

      {/* Buy button */}
      {product.purchase_url && (
        <a
          href={product.purchase_url}
          target="_blank"
          rel="noopener noreferrer"
          className="block text-center text-xs tracking-widest uppercase py-2.5 border border-black hover:bg-black hover:text-white transition-colors duration-200"
        >
          Shop
        </a>
      )}
    </div>
  )
}
