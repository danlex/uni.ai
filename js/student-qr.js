const dialog = document.getElementById('student-qr-dialog');
const openButton = document.getElementById('student-qr-open');
const closeButton = dialog.querySelector('.student-qr-close');

function notify() { document.dispatchEvent(new Event('student-qr-toggle')); }
openButton.addEventListener('click', () => { dialog.showModal(); notify(); });
closeButton.addEventListener('click', () => dialog.close());
dialog.addEventListener('close', notify);
dialog.addEventListener('click', event => {
  if (event.target !== dialog) return;
  const bounds = dialog.getBoundingClientRect();
  if (event.clientX < bounds.left || event.clientX > bounds.right ||
      event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
});
dialog.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', () => dialog.close());
});
