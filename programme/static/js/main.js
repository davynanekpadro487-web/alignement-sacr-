document.addEventListener('DOMContentLoaded', () => {
    // ─── Menu Mobile ───
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    if (hamburger) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            const icon = hamburger.querySelector('i');
            if (navLinks.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    }

    // ─── Champ téléphone : chiffres uniquement ───
    const telInput = document.getElementById('telephone');
    if (telInput) {
        telInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '');
        });
    }

    // ─── Upload de fichier : prévisualisation + drag & drop ───
    const fileInput = document.getElementById('capture_paiement');
    const uploadArea = document.getElementById('upload-area');
    const uploadPreview = document.getElementById('upload-preview');

    if (fileInput && uploadArea) {
        const uploadText = uploadArea.querySelector('.upload-text');

        // Prévisualisation à la sélection de fichier
        fileInput.addEventListener('change', () => {
            const file = fileInput.files[0];
            if (!file) return;

            uploadText.textContent = file.name;
            uploadArea.classList.add('has-file');

            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    uploadPreview.innerHTML =
                        '<img src="' + e.target.result + '" alt="Aperçu" class="upload-preview-img">';
                };
                reader.readAsDataURL(file);
            } else {
                uploadPreview.innerHTML =
                    '<i class="fa-solid fa-file-pdf upload-preview-pdf"></i>' +
                    '<span class="upload-preview-name">' + file.name + '</span>';
            }
        });

        // Drag & Drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => {
            uploadArea.addEventListener(evt, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        ['dragenter', 'dragover'].forEach(evt => {
            uploadArea.addEventListener(evt, () => uploadArea.classList.add('drag-over'));
        });

        ['dragleave', 'drop'].forEach(evt => {
            uploadArea.addEventListener(evt, () => uploadArea.classList.remove('drag-over'));
        });

        uploadArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length) {
                fileInput.files = files;
                fileInput.dispatchEvent(new Event('change'));
            }
        });
    }

    // ─── Animation au Scroll (Reveal) ───
    const els = document.querySelectorAll('.reveal');
    if (els.length > 0) {
        const io = new IntersectionObserver((entries) => {
            entries.forEach(e => {
                if (e.isIntersecting) {
                    e.target.classList.add('is-visible');
                    io.unobserve(e.target);
                }
            });
        }, { threshold: 0.15 });
        els.forEach(el => io.observe(el));
    }
});
