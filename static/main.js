document.addEventListener('DOMContentLoaded', function() {
    // Initialize based on current page
    const path = window.location.pathname;
    
    if (path.includes('/detect')) {
        initDetectionPage();
    } else if (path.includes('/verify')) {
        initVerificationPage();
    } else if (path.includes('/result')) {
        initResultPage();
    } else if (path.includes('/admin')) {
        initAdminPage();
    }
});

function initDetectionPage() {
    // Elements
    const videoFeed = document.getElementById('video-feed');
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const uploadBtn = document.getElementById('upload-btn');
    const detectionResult = document.getElementById('detection-result');
    const croppedImage = document.getElementById('cropped-image');
    const confidenceValue = document.getElementById('confidence-value');
    const proceedBtn = document.getElementById('proceed-btn');
    const recropBtn = document.getElementById('recrop-btn');
    const errorMessage = document.getElementById('error-message');
    
    // Event listeners
    uploadBtn.addEventListener('click', handleFileUpload);
    proceedBtn.addEventListener('click', proceedToVerification);
    recropBtn.addEventListener('click', resetDetection);
    
    // Functions
    function handleFileUpload() {
        if (fileInput.files.length === 0) {
            showError('Please select an image file');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        fetch('/detect', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showDetectionResult(data);
            } else {
                showError(data.message || 'Detection failed');
            }
        })
        .catch(error => {
            showError('Error processing image: ' + error.message);
        });
    }
    
    function showDetectionResult(data) {
        croppedImage.src = data.cropped_image;
        confidenceValue.textContent = data.confidence.toFixed(2);
        detectionResult.style.display = 'block';
        uploadForm.style.display = 'none';
    }
    
    function proceedToVerification() {
        window.location.href = '/verify';
    }
    
    function resetDetection() {
        detectionResult.style.display = 'none';
        uploadForm.style.display = 'block';
        fileInput.value = '';
    }
    
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }
}

function initVerificationPage() {
    // Elements
    const verifyForm = document.getElementById('verify-form');
    const extractionStatus = document.getElementById('extraction-status');
    const verificationResult = document.getElementById('verification-result');
    
    // Start extraction immediately when page loads
    extractLicenseDetails();
    
    function extractLicenseDetails() {
        fetch('/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                displayExtractedData(data.license_data);
            } else {
                showError('Extraction failed. Please try again.');
            }
        })
        .catch(error => {
            showError('Error during extraction: ' + error.message);
        });
    }
    
    function displayExtractedData(data) {
        document.getElementById('dl-number').value = data.dl_number || '';
        document.getElementById('name').value = data.name || '';
        document.getElementById('valid-till').value = data.valid_till || '';
        
        extractionStatus.style.display = 'none';
        verificationResult.style.display = 'block';
    }
    
    verifyForm.addEventListener('submit', function(e) {
        e.preventDefault();
        verifyAgainstDatabase();
    });
    
    function verifyAgainstDatabase() {
        const formData = {
            dl_number: document.getElementById('dl-number').value,
            name: document.getElementById('name').value,
            valid_till: document.getElementById('valid-till').value
        };
        
        fetch('/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = '/result';
            } else {
                showError('Verification failed: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            showError('Error during verification: ' + error.message);
        });
    }
}

function initResultPage() {
    // Get data from hidden elements or session
    const successResult = document.getElementById('success-result');
    const expiredResult = document.getElementById('expired-result');
    const deniedResult = document.getElementById('denied-result');
    
    // In a real app, you would fetch this from an API or use templating
    // For now, we'll assume the data is embedded in the page
    
    // Show appropriate result based on verification outcome
    if (document.body.dataset.result === 'success') {
        document.getElementById('result-name').textContent = document.body.dataset.name;
        document.getElementById('result-dl-number').textContent = document.body.dataset.dlNumber;
        document.getElementById('result-valid-till').textContent = document.body.dataset.validTill;
        successResult.style.display = 'block';
    } else if (document.body.dataset.result === 'expired') {
        expiredResult.style.display = 'block';
    } else {
        deniedResult.style.display = 'block';
    }
}

function initAdminPage() {
    const adminForm = document.querySelector('#admin form');
    
    adminForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const password = document.getElementById('password').value;
        
        fetch('/admin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `password=${encodeURIComponent(password)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = '/result?verified=true';
            } else {
                showError(data.message || 'Verification failed');
            }
        })
        .catch(error => {
            showError('Error: ' + error.message);
        });
    });
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}