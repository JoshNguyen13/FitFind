import type { Product } from '@/types'

export default function ProductCard({ product }: { product: Product }) {
  return (
    <div className="group flex flex-col">
      {/* Image */}
      <div className="aspect-3/4 bg-gray-100 rounded-lg overflow-hidden mb-3">
        {product.image_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={product.image_url}
            alt={product.product_title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-300 text-xs">
            No image
          </div>
        )}
      </div>

      {/* Info */}
      <div className="flex-1 flex flex-col gap-1">
        {product.brand && (
          <p className="text-xs text-gray-400 font-medium uppercase tracking-wide">
            {product.brand}
          </p>
        )}
        <p className="text-sm font-medium leading-snug line-clamp-2 flex-1">
          {product.product_title}
        </p>
        <p className="text-sm font-semibold">
          {product.price != null ? `$${product.price.toFixed(2)}` : 'See price'}
        </p>
      </div>

      {/* Buy button */}
      {product.purchase_url && (
        <a
          href={product.purchase_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-3 block text-center text-xs font-semibold bg-black text-white py-2.5 rounded-md hover:bg-gray-800 transition-colors"
        >
          Buy
        </a>
      )}
    </div>
  )
}
