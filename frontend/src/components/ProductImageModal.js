import React from 'react';
import { X } from 'lucide-react';

const ProductImageModal = ({ product, isOpen, onClose }) => {
  if (!isOpen) return null;

  // Use img_big_my with fallback to img_big_pish
  const imageUrl = product.img_big_my || product.img_big_pish || product.img_small;

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-2xl max-w-2xl w-full p-6 relative"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 hover:bg-gray-100 rounded-full transition-colors"
        >
          <X size={24} />
        </button>

        <div className="flex flex-col items-center">
          {imageUrl ? (
            <>
              <img 
                src={imageUrl}
                alt={`${product.brand} ${product.model}`}
                className="w-full max-w-md h-auto object-contain mb-4"
                onError={(e) => {
                  e.target.src = product.img_small || '';
                }}
              />
              <div className="text-center">
                <h3 className="text-2xl font-bold text-gray-900 mb-2">{product.brand}</h3>
                <p className="text-lg text-gray-600 mb-4">{product.model}</p>
                {product.width && product.diameter && (
                  <p className="text-gray-700">
                    {product.height 
                      ? `${product.width}/${product.height} R${product.diameter}`
                      : `${product.width}x${product.diameter}`
                    }
                  </p>
                )}
              </div>
            </>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">Изображение недоступно</p>
              <div className="mt-4">
                <h3 className="text-xl font-bold text-gray-900">{product.brand}</h3>
                <p className="text-gray-600">{product.model}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductImageModal;
