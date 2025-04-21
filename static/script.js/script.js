function formatDoc(cmd, value=null) {
	if(value) {
		document.execCommand(cmd, false, value);
	} else {
		document.execCommand(cmd);
	}
}

function addLink() {
	const url = prompt('Insert url');
	formatDoc('createLink', url);
}




const content = document.getElementById('content');

content.addEventListener('mouseenter', function () {
	const a = content.querySelectorAll('a');
	a.forEach(item=> {
		item.addEventListener('mouseenter', function () {
			content.setAttribute('contenteditable', false);
			item.target = '_blank';
		})
		item.addEventListener('mouseleave', function () {
			content.setAttribute('contenteditable', true);
		})
	})
})


const showCode = document.getElementById('show-code');
let active = false;

showCode.addEventListener('click', function () {
	showCode.dataset.active = !active;
	active = !active
	if(active) {
		content.textContent = content.innerHTML;
		content.setAttribute('contenteditable', false);
	} else {
		content.innerHTML = content.textContent;
		content.setAttribute('contenteditable', true);
	}
})



const filename = document.getElementById('filename');

function fileHandle(value) {
	if(value === 'new') {
		content.innerHTML = '';
		filename.value = 'untitled';
	} else if(value === 'txt') {
		const blob = new Blob([content.innerText])
		const url = URL.createObjectURL(blob)
		const link = document.createElement('a');
		link.href = url;
		link.download = `${filename.value}.txt`;
		link.click();
	} else if(value === 'pdf') {
		html2pdf(content).save(filename.value);
	}
}
function uploadImage() {
    // Create a file input element dynamically
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*'; // Accept only images
    
    // When a file is selected, create an image element
    input.addEventListener('change', function () {
        const file = input.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                // Create an image element
                const img = document.createElement('img');
                img.src = e.target.result; // Set image source to uploaded file
                img.style.maxWidth = '100%'; // Optionally, set a max width for the image
                img.style.height = 'auto'; // Maintain aspect ratio
                insertImageAtCursor(img);
            };
            reader.readAsDataURL(file); // Read the file as a data URL
        }
    });

    // Trigger the file input click event to open the file picker
    input.click();
}

function insertImageAtCursor(img) {
    // Get the current editable content area
    const content = document.getElementById('content');
    
    // Get the current selection
    const selection = window.getSelection();
    const range = selection.getRangeAt(0);

    // Insert the image at the cursor position
    range.deleteContents(); // Remove selected text if any
    range.insertNode(img); // Insert the image

    // After inserting the image, move the cursor after the image
    range.setStartAfter(img);
    range.setEndAfter(img);
    selection.removeAllRanges();
    selection.addRange(range);
}
