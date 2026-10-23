from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request):
    ocr_status = "ok"
    try:
        from rapidocr_onnxruntime import RapidOCR
        RapidOCR()
    except Exception as e:
        ocr_status = f"unavailable: {e}"
    return JsonResponse({"status": "ok", "ocr": ocr_status})


urlpatterns = [
    path('health', health_check),
    path('health/', health_check),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
