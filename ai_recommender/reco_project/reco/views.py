# reco/views.py
from django.http import JsonResponse
from .utils.recommender import recommend_for_user_with_meta

def recommend_view(request, user_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return JsonResponse({'error': 'user_id invalid'}, status=400)

    recs = recommend_for_user_with_meta(user_id, top_n=5)
    return JsonResponse({'user_id': user_id, 'recommendations': recs})