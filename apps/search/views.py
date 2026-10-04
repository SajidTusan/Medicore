from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import global_search


@login_required
def global_search_view(request):
    query = request.GET.get("q", "").strip()

    results = global_search(
        query=query,
        user=request.user,
    )

    total_results = sum(
        len(items)
        for items in results.values()
    )

    return render(
        request,
        "search/results.html",
        {
            "query": query,
            "results": results,
            "total_results": total_results,
        },
    )