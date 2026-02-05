import random
from typing import List, Tuple

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import DrawHistory, Prize, RouletteConfig

PALETTE = [
    '#F59E0B',
    '#FDE047',
    '#86EFAC',
    '#22C55E',
    '#A7F3D0',
    '#FCD34D',
    '#FDBA74',
    '#F97316',
    '#FCA5A5',
    '#FB7185',
    '#FBBF24',
    '#4ADE80',
]


def build_segments(prizes: List[Prize]) -> Tuple[str, List[dict], List[dict]]:
    usable = [p for p in prizes if p.probability and p.probability > 0]
    total = sum(p.probability for p in usable)
    if total <= 0:
        return "conic-gradient(#E5E7EB 0deg 360deg)", [], []

    segments = []
    gradient_parts = []
    start = 0.0
    color_idx = 0
    for prize in usable:
        angle = prize.probability / total * 360.0
        end = start + angle
        color = PALETTE[color_idx % len(PALETTE)]
        gradient_parts.append(f"{color} {start:.2f}deg {end:.2f}deg")
        segments.append({
            'prize': prize,
            'start': start,
            'end': end,
            'mid': (start + end) / 2.0,
        })
        start = end
        color_idx += 1

    gradient = "conic-gradient(from -90deg, " + ", ".join(gradient_parts) + ")"
    labels = [{'name': s['prize'].name, 'angle': s['mid']} for s in segments]
    return gradient, labels, segments


def frontend(request: HttpRequest) -> HttpResponse:
    configs = list(RouletteConfig.objects.all().order_by('-updated_at'))
    config_id = request.GET.get('config')
    selected = None
    if config_id:
        selected = RouletteConfig.objects.filter(id=config_id).first()
    if selected is None and configs:
        selected = configs[0]

    prizes = list(selected.prizes.all()) if selected else []
    wheel_gradient, labels, _ = build_segments(prizes)
    history = list(DrawHistory.objects.filter(config=selected)[:10]) if selected else []

    context = {
        'configs': configs,
        'selected': selected,
        'wheel_gradient': wheel_gradient,
        'labels': labels,
        'history': history,
    }
    return render(request, 'frontend.html', context)


@login_required
def backend(request: HttpRequest) -> HttpResponse:
    configs = list(RouletteConfig.objects.all().order_by('-updated_at'))
    config_id = request.GET.get('config') or request.POST.get('config_id')
    selected = None
    if config_id:
        selected = RouletteConfig.objects.filter(id=config_id).first()
    if selected is None and configs:
        selected = configs[0]

    if request.method == 'POST':
        name = (request.POST.get('config_name') or '').strip()
        config_id = request.POST.get('config_id')
        if config_id:
            config = RouletteConfig.objects.filter(id=config_id).first()
            if config:
                config.name = name or config.name
                config.save()
            else:
                config = RouletteConfig.objects.create(name=name or '未命名抽獎')
        else:
            config = RouletteConfig.objects.create(name=name or '未命名抽獎')

        names = request.POST.getlist('prize_name')
        probs = request.POST.getlist('prize_prob')
        Prize.objects.filter(config=config).delete()
        for idx, (n, p) in enumerate(zip(names, probs)):
            n = (n or '').strip()
            p = (p or '').strip()
            if not n or not p:
                continue
            try:
                prob = float(p)
            except ValueError:
                continue
            Prize.objects.create(config=config, name=n, probability=prob, order=idx)

        return redirect(f'/backend/?config={config.id}')

    prizes = list(selected.prizes.all()) if selected else []
    context = {
        'configs': configs,
        'selected': selected,
        'prizes': prizes,
    }
    return render(request, 'backend.html', context)


@require_POST
def api_draw(request: HttpRequest) -> JsonResponse:
    config_id = request.POST.get('config_id')
    nickname = (request.POST.get('nickname') or '').strip()
    if not config_id or not nickname:
        return JsonResponse({'success': False, 'message': '請輸入暱稱並選擇抽獎內容'})

    config = RouletteConfig.objects.filter(id=config_id).first()
    if not config:
        return JsonResponse({'success': False, 'message': '找不到抽獎內容'})

    prizes = list(config.prizes.all())
    wheel_gradient, labels, segments = build_segments(prizes)
    if not segments:
        return JsonResponse({'success': False, 'message': '尚未設定獎項或機率'})

    total = sum(s['prize'].probability for s in segments)
    r = random.uniform(0, total)
    acc = 0.0
    selected = segments[-1]
    for seg in segments:
        acc += seg['prize'].probability
        if r <= acc:
            selected = seg
            break

    DrawHistory.objects.create(
        config=config,
        nickname=nickname,
        prize_name=selected['prize'].name,
    )

    history = list(DrawHistory.objects.filter(config=config)[:10])
    history_payload = [
        {
            'time': h.created_at.astimezone().strftime('%H:%M'),
            'prize': h.prize_name,
            'nickname': h.nickname,
        }
        for h in history
    ]

    return JsonResponse({
        'success': True,
        'prize': selected['prize'].name,
        'target_angle': round(selected['mid'], 2),
        'history': history_payload,
    })
