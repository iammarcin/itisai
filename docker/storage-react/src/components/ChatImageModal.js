// ImageModal.js

import React from 'react';
import './css/ChatImageModal.css';

const ChatImageModal = ({ images, currentIndex, onClose, onNext, onPrev }) => {
  if (!images || images.length === 0) return null;

  return (
    <div className="image-modal">
      <div className="image-modal-content">
        <span className="close" onClick={onClose}>&times;</span>
        <img src={images[currentIndex]} alt="Chat" className="modal-image" />
        {images.length > 1 && (
          <>
            <button className="prev" onClick={onPrev}>&#10094;</button>
            <button className="next" onClick={onNext}>&#10095;</button>
          </>
        )}
      </div>
    </div>
  );
};

export default ChatImageModal;
