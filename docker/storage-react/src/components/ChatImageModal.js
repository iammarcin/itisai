import React, { useEffect, useRef } from 'react';
import './css/ChatImageModal.css';

// this will be used to display images (attached to chat or image of AI character) or charts (from Health section)
// if its image - just display
// if its AI character - display with description and name
// isChart - important - because different way to handle images and charts
// by default false
const ChatImageModal = ({ images, currentIndex, onClose, onNext, onPrev, characterName = null, characterDescription = null, isChart = false }) => {
  const modalRef = useRef(null);

  useEffect(() => {
    if (!isChart) return;
    // Resize canvas elements in the modal
    const resizeCanvas = () => {
      const canvasElements = document.querySelectorAll('.image-modal-content canvas');
      canvasElements.forEach(canvas => {
        canvas.style.width = '100%';
        canvas.style.height = '80vh';
      });
    };

    resizeCanvas();
  }, [currentIndex]);

  // resize upon displaying the chart
  useEffect(() => {
    if (isChart) {
      window.dispatchEvent(new Event('resize'));
    }
  }, [isChart, currentIndex]);


  const handleKeyDown = (e) => {
    if (e.key === 'Escape') onClose();
    if (e.key === 'ArrowRight') onNext();
    if (e.key === 'ArrowLeft') onPrev();
  };

  // click outside / hit keyboard listener
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (modalRef.current && !modalRef.current.contains(event.target)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [onClose]);

  if (!images || images.length === 0) return null;

  return (
    <div className="image-modal">
      <div className="image-modal-content" ref={modalRef}>
        <span className="close" onClick={onClose}>&times;</span>
        {isChart ? (
          <div className="modal-chart">
            {images[currentIndex]}
          </div>
        ) : (
          <img src={images[currentIndex]} alt="Chat" className="modal-image" />
        )}
        {characterName && <div className="modal-character-name">{characterName}</div>}
        {characterDescription && <div className="modal-character-description">{characterDescription}</div>}
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
