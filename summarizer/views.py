import os
import tempfile
from django.shortcuts import render
from .forms import UploadForm
from .utils import pdf_to_image, load_image, preprocess_image_cv2, ocr_image, call_openai_for_summary

def upload_view(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            age = form.cleaned_data.get('age')
            gender = form.cleaned_data.get('gender')

            # Save file temporarily
            tmp_dir = tempfile.mkdtemp()
            tmp_path = os.path.join(tmp_dir, uploaded_file.name)
            with open(tmp_path, 'wb') as dest:
                for chunk in uploaded_file.chunks():
                    dest.write(chunk)

            # Convert if PDF
            ext = os.path.splitext(tmp_path)[1].lower()
            if ext == '.pdf':
                pil_img = pdf_to_image(tmp_path)
                cv_img = load_image(pil_img)
            else:
                cv_img = load_image(tmp_path)

            # Preprocess + OCR
            processed = preprocess_image_cv2(cv_img)
            ocr_text = ocr_image(processed)

            # LLM summarization
            summary_json = call_openai_for_summary(ocr_text, age=age, gender=gender)

            # Cleanup
            try:
                os.remove(tmp_path)
            except OSError:
                pass

            return render(request, 'summarizer/result.html', {
                "ocr_text": ocr_text,
                "summary": summary_json
            })
    else:
        form = UploadForm()

    return render(request, 'summarizer/upload.html', {'form': form})
