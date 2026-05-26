document.addEventListener('DOMContentLoaded', async () => {
    document.addEventListener('keydown', function (event) {
        if (event.key === 'F5' || event.key === 'Escape') {
            event.preventDefault();
            window.location.href = '/upload';
        }
    });
    const fileListWrapper = document.getElementById('file-list-wrapper');
    const uploadRedirectButton = document.getElementById('upload-tab-btn');

    const updateTabStyles = () => {
        const uploadTab = document.getElementById('upload-tab-btn');
        const imagesTab = document.getElementById('images-tab-btn');

        const isImagesPage = window.location.pathname.includes('images');

        uploadTab.classList.remove('upload__tab--active');
        imagesTab.classList.remove('upload__tab--active');

        if (isImagesPage) {
            imagesTab.classList.add('upload__tab--active');
        } else {
            uploadTab.classList.add('upload__tab--active');
        }
    };



    const displayFiles = async () => {
        const storedFiles = await fetch('/api/images-data/').then(res => res.json()).then(data => data.images);
        fileListWrapper.innerHTML = '';

        if (storedFiles.length === 0) {
            fileListWrapper.innerHTML = '<p class="upload__promt" style="text-align: center; margin-top: 50px;">No images uploaded yet.</p>';
        } else {
            const container = document.createElement('div');
            container.className = 'file-list-container';
            const header = document.createElement('div');
            header.className = 'file-list-header';
            header.innerHTML = `
                <div class="file-col file-col-image">Image</div>
                <div class="file-col file-col-name">Name</div>
                <div class="file-col file-col-url">Url</div>
                <div class="file-col file-col-delete">Delete</div>
            `;
            container.appendChild(header);

            const list = document.createElement('div');
            list.id = 'file-list';

            storedFiles.forEach((image) => {
                const imageUrl = `${window.location.origin}/images/${image.filename}.${image.file_type}`;
                const fileItem = document.createElement('div');
                fileItem.className = 'file-list-item';
                fileItem.innerHTML = `
                    <div class="file-col file-col-image">
                        <img src="${imageUrl}" alt="file icon" width="20%">
                    </div>
                    <div class="file-col file-col-name">
                        <span class="file-name">${image.original_name}</span>
                    </div>
                    <div class="file-col file-col-url"><a href="${imageUrl}" target="_blank">${imageUrl}</a></div>
                    <div class="file-col file-col-delete">
                        <button data-filename="${image.filename}.${image.file_type}" class="delete-btn"><img src="/static/image-uploader/img/icon/delete.png" alt="delete icon"></button>
                    </div>
                `;
                list.appendChild(fileItem);
            });

            container.appendChild(list);
            fileListWrapper.appendChild(container);
            addDeleteListeners();
        }

        updateTabStyles();
    };

    const addDeleteListeners = async () => {
        document.querySelectorAll('.delete-btn').forEach(async (button) => {
            button.addEventListener('click', async (event) => {
                const filename = event.currentTarget.dataset.filename;
                await fetch(`/api/images/${filename}`, { method: 'DELETE'})
                    .then(() => { displayFiles(); })
                    .catch(() => { console.log('File deletion failed')})
            });
        });
    };

    if (uploadRedirectButton) {
        uploadRedirectButton.addEventListener('click', () => {
            window.location.href = '/upload';
        });
    }

    displayFiles();
});