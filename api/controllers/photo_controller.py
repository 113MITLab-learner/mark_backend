# api/controllers/photo_controller.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.paginator import Paginator
from ..models import Photo, AVAILABLE_LABELS
from django.db.models import Q

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_photos(request):
    try:
        # 取得查詢參數
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 20)
        label_filter = request.GET.get('label', None)
        show_unlabeled = request.GET.get('show_unlabeled', 'false').lower() == 'true'

        photos_query = Photo.objects.filter(user=request.user).order_by('-uploaded_at')

        # 如果有 label_filter，過濾包含此標籤的照片
        if label_filter and label_filter in AVAILABLE_LABELS:
            # 假設 label 欄位以逗號分隔標籤字串，檢查該字串中是否包含指定標籤
            photos_query = photos_query.filter(label__icontains=label_filter)

        # 如果 show_unlabeled 為真，過濾沒有標籤的照片
        if show_unlabeled:
            photos_query = photos_query.filter(Q(label__isnull=True) | Q(label=''))

        paginator = Paginator(photos_query, page_size)
        current_page = paginator.get_page(page)

        photos_data = [{
            'id': photo.id,
            'image_url': request.build_absolute_uri(photo.image.url),
            'uploaded_at': photo.uploaded_at,
            'processed_image_url': photo.processed_image.url if photo.processed_image else None,
            'label': photo.label.split(',') if photo.label else []
        } for photo in current_page]

        return Response({
            "photos": photos_data,
            "available_labels": AVAILABLE_LABELS,
            "total_photos": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": current_page.number
        }, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_label_photos(request):
    try:
        photo_ids = request.data.get('photo_ids', [])
        new_label = request.data.get('label', None)

        if not photo_ids or not new_label:
            return Response({"error": "缺少 photo_ids 或 label"}, status=400)

        if new_label not in AVAILABLE_LABELS:
            return Response({"error": "標籤不在預定義的集合中"}, status=400)

        # 批次更新標籤
        photos = Photo.objects.filter(id__in=photo_ids, user=request.user)
        for p in photos:
            current_labels = p.label.split(',') if p.label else []
            if new_label not in current_labels:
                current_labels.append(new_label)
            p.label = ','.join(filter(None, current_labels))
            p.save()

        return Response({"message": "批次標籤成功"}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_delete_photos(request):
    try:
        photo_ids = request.data.get('photo_ids', [])
        if not photo_ids:
            return Response({"error": "缺少 photo_ids"}, status=400)

        photos = Photo.objects.filter(id__in=photo_ids, user=request.user)
        deleted_count = 0
        # 個別呼叫 delete 以觸發 Photo model 中的 delete() 方法並刪除檔案
        for photo in photos:
            photo.delete()
            deleted_count += 1

        return Response({"message": f"已刪除 {deleted_count} 張照片"}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
