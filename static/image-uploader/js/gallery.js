document.addEventListener('DOMContentLoaded', async () => {
  const grid = document.getElementById('grid');
  const empty = document.getElementById('empty');
  
  const uploadBtn = document.getElementById('upload-tab-btn');
  const imagesBtn = document.getElementById('images-tab-btn');
  if (uploadBtn) uploadBtn.addEventListener('click', () => (window.location.href = '/upload'));
  if (imagesBtn) imagesBtn.addEventListener('click', () => (window.location.href = '/images?page=1'));
 
  const prev = document.getElementById('prev');
  const next = document.getElementById('next');
  if (prev) prev.style.display = 'none';
  if (next) next.style.display = 'none';
  const renderImages = (images) => {
    images.forEach((img) => {
      const url = `${window.location.origin}/images/${img.filename}.${img.file_type}`;
      const card = document.createElement('div');
      card.className = 'gallery-card';
      card.innerHTML = `
  <a href="${url}" target="_blank" rel="noreferrer">
    <img src="${url}" alt="${img.original_name}">
  </a>
`;
      grid.appendChild(card);
    });
  };
  let page = 1;
  let total = 0;
  while (true) {
    const res = await fetch(`/api/images-data/?page=${page}`).then((r) => r.json());
    const images = res.images || [];
    total += images.length;
    renderImages(images);
    if (!res.has_next) break;
    page += 1;
  }
  if (total === 0) {
    empty.style.display = 'block';
  }
});