// misc.js

const formatDate = (dateString) => {
 const date = new Date(dateString);
 const year = date.getFullYear();
 const month = String(date.getMonth() + 1).padStart(2, '0');
 const day = String(date.getDate()).padStart(2, '0');
 const hours = String(date.getHours()).padStart(2, '0');
 const minutes = String(date.getMinutes()).padStart(2, '0');
 return `${year}-${month}-${day} ${hours}:${minutes}`;
};

/*
const scrollToBottom = (option) => {
 const isAtBottom = Math.ceil(window.innerHeight + window.scrollY + 50) >= document.documentElement.scrollHeight;

 if (isAtBottom) {
  if (!isMobile && option === "streaming") {
   const botTextAreaContainer = document.querySelector('.botTextAreaContainer');

   if (messagesEndRef.current && botTextAreaContainer) {
    // Calculate the position just above the botTextAreaContainer
    const scrollTargetPosition =
     botTextAreaContainer.getBoundingClientRect().top - window.innerHeight + botTextAreaContainer.offsetHeight;

    // Scroll smoothly to the target position
    window.scrollBy({
     top: scrollTargetPosition,
     behavior: 'smooth',
    });
   }
  } else {
   if (messagesEndRef.current) {
    messagesEndRef.current?.scrollIntoView({
     behavior: "smooth",
    });
   }
  }
 }

};*/

export { formatDate };